# ---- Base --------------------------------------------------------
FROM python:3.12 as builder
LABEL maintainer="Tyler Williams"

# Add app user
ARG APPLICATION_USER=user
RUN adduser -u 1000 --disabled-password ${APPLICATION_USER}

ENV PYTHONUNBUFFERED 1
ENV IS_BUILDING=True
ENV PATH="/root/.cargo/bin:$PATH"

RUN mkdir -p /project \
    && mkdir -p /venv \
    && mkdir -p /project/notebooks \
    && mkdir -p /requirements \
    # Install additional tools needed for building and testing
    && apt-get update -qq -y \
    && apt-get install -qq -y libpq-dev \
    libaio1 \
    build-essential \
    git \
    bash \
    make \
    python3-dev \
    curl

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

RUN uv venv /venv \
    && . /venv/bin/activate \
    && uv pip install pip \
    && uv pip install setuptools \
    && uv pip install wheel \
    && uv pip install gitpython==3.1.43

RUN apt-get clean

# Make sure git and cicd_tool python libraries are installed
RUN chown -R ${APPLICATION_USER}:${APPLICATION_USER} /project \
    && chown -R ${APPLICATION_USER}:${APPLICATION_USER} /requirements \
    && chown -R ${APPLICATION_USER}:${APPLICATION_USER} /venv


WORKDIR /project

COPY entrypoint.sh /usr/bin/.entrypoint.sh
RUN chmod +x /usr/bin/.entrypoint.sh

# Copy the application code
COPY stuco_app /project/stuco_app
COPY pyproject.toml poetry.lock manage.py gunicorn-cfg.py /project/
COPY config /project/config
COPY tests /project/tests
COPY .spg /project/.spg
COPY docs /project/docs
COPY core /project/core
COPY static /project/static
COPY templates /project/templates
COPY users /project/users

USER root

# Set the user to 'user' for better security
USER ${APPLICATION_USER}

ENTRYPOINT ["/usr/bin/.entrypoint.sh"]
CMD ["default"]


# ---- Final -------------------------------------------------------
FROM python:3.12 as final
LABEL maintainer="Tyler Williams"

ENV PYTHONUNBUFFERED 1
ENV PYTHON=python3.10
ENV PATH="/venv/bin:$PATH"

# Copy the application code
COPY --from=builder /project/pyproject.toml \
    /project/poetry.lock \
    /project/gunicorn-cfg.py \
    /project/manage.py /project/

COPY --from=builder /project/stuco_app /project/stuco_app/
COPY --from=builder /project/config /project/config/
COPY --from=builder /project/core /project/core/
COPY --from=builder /project/static /project/static/
COPY --from=builder /project/staticfiles /project/staticfiles/
COPY --from=builder /project/templates /project/templates/
COPY --from=builder /project/users /project/users/
COPY --from=builder /venv /venv
COPY --from=builder /project/gunicorn-cfg.py /project/gunicorn-cfg.py

RUN chown -R user:user /project

CMD ["gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi"]

# Set the user to 'app' for better security
USER user

# End of final stage

# ---- Test --------------------------------------------------------------
FROM builder as test
LABEL maintainer="Tyler Williams"

ENV PYTHONUNBUFFERED 1

ENV PATH="/venv/bin:/poetry_venv/bin:$PATH"

# Install the dev dependencies
# RUN /venv/bin/python -m pip install -r /requirements/requirements-dev.txt

# Copy the application supporting directories
COPY --from=builder /project/.spg /project/.spg
COPY --from=builder /project/config /project/config
COPY --from=builder /project/docs /project/docs
COPY --from=builder /project/tests /project/tests
COPY --from=builder /venv /venv
# COPY --from=builder /poetry_venv /poetry_venv

USER root

# Make sure the user 'user' owns the project directory
RUN chown -R user:user /project

# Set the user to 'user' for better security
USER user

# End of test stage
