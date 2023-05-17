# Introduction
In this activity you will launch the API you created in your k8s namespace. You will be using all of the skills you learned in this course to modify our pipeline with the new API. If working in a group take turns with the steps. A sample app is provided if you need a working one to deploy.

We will only be updating the dev environment to test our new API. The provided API is a currency converter API. After deploying it, your team will add functionality to that API by creating new endpoints. The new endpoints will allow you to get quotes from crypto-currencies, and insert them into the orderbook application. You will add more endpoints but first lets focus on the deployment!

# Instructions

## Adding Source Code to GitHub

1. Create a new `branch` for the [orderbook](https://github.com/The-Software-Guild/pss-orderbook-deploy) app, or use your existing on that is part of the jenkins pipeline.
    ```
    git clone https://github.com/The-Software-Guild/pss-orderbook-deploy
    cd pss-orderbook-deploy
    git checkout -b <COHORT><TEAM>
    ```

2. Create a new folder in `src` named after the API. 
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
    SQLAlchemy==2.0.4
    pymysql==1.0.2
    cryptography==39.0.2
    ```

5. Create a dockerfile in `Dockerfiles` named Dockerfile_CurrencyAPI 
    ```
    vi Dockerfiles/Dockerfile_currencyAPI
    ```

    Paste the docker instructions below.

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
    A common error is curly brackets, make sure to follow the convention of the file.

2. Push your changes.

3. Log into [jenkins](https://jenkins.computerlab.online/) and locate your pipeline settings. Update or confirm the pipelines branch matches the one you make your code changes to.

4. Execute the pipeline and monitor for errors. Common errors are curly brackets in the Jenkinsfile or using the wrong nameing convention. When you see your newly created image in the [ecr-list](http://ecrlist-ps.computerlab.online/index.php) with the name you used for destination above, your delievery pipeline has been updated.

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

4. Create three files to deploy this application.
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
    {namespace="<COHORT>-<TEAM>-dev", container="currencyapi"} |= ``
    ```

# Assesment

Now that you have lanched the application you will need to add endpoints to the new API and connect the orderbook API. After doing so, prepare a 10-15 minute presentation explaining the change you  made.

- Go through the `app.py` file and implement each endpoint under the `# @CODE` comment.
- Each team member should code at least one endpoint.
- Make sure each endpoint in the file has a doc string and that it explains the endpoint, and names the team member who implemented it.

To achieve a perfect mark you must implement all endpoints, account for errors, and present your powerpoint. Grading will be done at the discretion of the instructor. Be sure to include the different systems your API connects too and how they were used by your API.

# Rubric

You will be marked out of 100. The table below describes how.   




| Deployment | Endpoints                      | Presentation |
| ---------- | ------------------------------- | ----------- |
| 50 points  | 30 points                      | 20 points    |
| ---------- | ------------------------------ | ------------- |
|            | - Each team member              |                |
|     world       | coded at least one       |             hello          |
|            | endpoint                 |                       |
|            | - All endpoints are          |                   |
