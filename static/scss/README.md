## How to use SASS to "customize" the Bootstrap Look and Feel

---

1. First you need to run **npm install** to install the npm packages described in **package.json**

    - To do so, you may use the Node docker image (**make sure you execute from the root directory of this repo**) with a command like:
    ```
    docker run -it --rm --name node -p 3000:3000 -v "$PWD":/usr/src/app -w /usr/src/app node:latest npm install
    ```
2. Then you can use the **sassdockerfile** to create a sass tool image by executing the following command from **this** directory:

    ```
    docker build -f sassdockerfile -t sass .
    ```
3. To continuously "watch" for changes to scss files (and auto-compile them to css files), you may run the **sass** docker image that you created in step 2, by executing the following command (**make sure you execute from the root directory of this repo**):

    ```
    docker run --rm -it --init -v $(PWD):/app sass dart ./bin/sass.dart --watch --poll /app/static/scss:/app/static/css
    ```

---

Look at **"node_modules/bootstrap/dist/scss/_variables.scss"** to see the variables that you can overwrite in your **"scss/bootstrap.scss"** file. For any custom styles, add them to the **"scss/styles.scss"** file.

#### Do not edit the CSS files directly.
