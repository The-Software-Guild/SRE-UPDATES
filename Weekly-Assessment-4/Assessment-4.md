# Introduction
In this activity you will launch the API you created in your k8s namespace. You will be using all of the skills you learned in this course to modify our pipeline with the new API. If working in a group take turns with the steps. A sample app is provided if you need a working one to deploy.

We will only be updating the dev environment to test our new API. This activity can be used to deploy any python FastAPI app, but uses the naming convention for the provided currency app. If you want to use a different naming convention, just be sure to replace the word "currency" with a more relevant name in each code sample.

# Instructions

## Adding Source Code to GitHub

1. Create a new `branch` for the [orderbook](https://github.com/The-Software-Guild/pss-orderbook-deploy) app.
    ```
    git clone https://github.com/The-Software-Guild/pss-orderbook-deploy
    cd pss-orderbook-deploy
    git checkout -b <COHORT><TEAM>
    ```

2. Create a new folder in `src` named after your API. 
    ```
    mkdir src/currencyAPI
    ```

3. Add your source code for API to this folder. Then list the contents of the app to verify it worked. Make sure your app is in a directory named app, and has an empty `__init__.py` file along with a `main.py` for the app. 
    ```
    cp -r /path/to/app src/currencyAPI
    ls -l src/currencyAPI/app
    # __init__.py  main.py
    ```

4. Create a `requirements.txt` with your pip installs inside the source code folder.
    ```
    vi src/currencyAPI/requirements.txt
    ```

    Paste the each dependency of your app on a new line and save the file.

    ```
    fastapi==0.95.1
    uvicorn==0.21.1
    requests==2.29.0
    ```

5. Create a dockerfile in `Dockerfiles` named Dockerfile_CurrencyAPI 
    ```
    vi Dockerfiles/Dockerfile_currencyAPI
    ```

    Paste the docker instructions below. Be sure to use the correct API name.

    ```dockerfile
    FROM python:3.10.0
    WORKDIR /code
    COPY src/currencyAPI /code
    COPY src/currencyAPI/requirements.txt /code/requirements.txt 
    RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
    # uvicorn serves requests
    CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--workers", "2"]
    ```
6. Push to your branch, you may need to set the upstream origin if it is first push. Just follow the directions after git push in the standard output.

    ```
    git status
    git add --all
    git commit -m"Adding currency API to branch "
    git push
    ```

## Updating Pipeline

1. Within your branch, update the `Jenkinsfile` by adding another stage named after your API. You can do this by copying one of the other stages and updating the stage name and kaniko command. Below is an example of the updated kaniko command with the new dockerfile and destination. 

    ```sh
    /kaniko/executor -f `pwd`/Dockerfiles/Dockerfile_currencyAPI -c `pwd` --insecure --skip-tls-verify --cache=false --destination=${ECR_REPO}:${JOB_NAME}currency-api-dev-${BUILD_NUMBER}
    ```
    A common error is curly brackets, make sure to follow the convention of the file. Be sure to use an appropriate name in destination, it will be used later.

2. Push your changes.

3. Log into [jenkins](https://jenkins.computerlab.online/) and locate your pipeline settings. Update the branch to the new branch you created.

4. Execute the pipeline and monitor for errors. Common errors are curly brackets in the Jenkinsfile or using the wrong nameing convention. When you see your newly created image in the [ecr-list](http://ecrlist-ps.computerlab.online/index.php) with the name you used for --destination above, your delievery pipeline has been updated.

## Deploying to Dev

1. Change directory to the `sre-course-infra` repository.
    ```
    cd /path/to/sre-course-infra
    ```
2. Change directory to your enviornment.
    ```
    cd /flux/apps/eks-sre-course/<COHORT>-<TEAM>-dev
    ```
3. Use or create a branch for your team
    ```
    git checkout -b <COHORT><TEAM>-dev
    ```

4. Create three files to deploy this application. You can give these files more relevant names if deploying a different API.
    ```
    touch deployment-currencyapi.yaml service-currencyapi.yaml imgPolicy-currencyapi.yaml
    ```
5. Copy the code our devops team made into these files. 

    - Copy contents of `deployment-dev-template.yaml` into `deployment-currencyapi.yaml`.
    - `service-dev-template.yaml` to `service-currencyapi.yaml`.
    - `imgPolicy-template.yaml` to `imgPolicy-currencyapi.yaml`.

6. Update the templates. Use `sed` to replace `<COHORT>`,`<TEAM>` and `<API>` with the correct values. For example 
    ```sh
    sed -i 's/<API>/currency/g' deployment-currencyapi.yaml service-currencyapi.yaml imgPolicy-currencyapi.yaml

    # sed on <COHORT>

    # sed on <TEAM>
    ```

7. Update the `ingress.yaml` file to make your service accessible over the internet. Be sure to use your cohort and team number for `<COHORT>` and `<TEAM>`.
    - Under `spec: tls: -hosts:` add a host for your new application, for example `<COHORT><TEAM>dev-currencyapi.computerlab.online`
    - User `spec: rules:` add a new host such as below
        ```
        - host: <COHORT><TEAM>dev-currencyapi.computerlab.online
          http:
            paths:
            - path: /
              pathType: Prefix
              backend:
                service:
                  name: currencyapi
                  port:
                    number: 8000
        ```

8. Push the changes
    ```
    git add service-currencyapi.yaml deployment-dev-sample.yaml imgPolicy-currency.yaml ingress.yaml
    git commit -m"Adding a new service to dev"
    git push
    ```
9. Create a PR and merge to main branch. 

10. Test your app with the URI creted in the ingress file and the `doc` endpoint such as `https://<COHORT><TEAM>dev-currencyapi.computerlab.online/docs`

## Troubleshooting
- Use the [k8s dashboard](https://k8sdashboard.computerlab.online/), search for your namespace at the top and wait for the deployment to be available.
- Monitor the logs in [Grafana](https://grafana.computerlab.online/) for erros. Under the explore (compass icon) tab you can select the `loki` data source and run these queries to see logs.

    For YAML errors
    ```
    {job="flux-system/kustomize-controller"} |= `<COHORT>-<TEAM>-dev`
    ```

    For application errors
    ```
    {namespace="<COHORT>-<TEAM>-dev"} |= ``
    ```