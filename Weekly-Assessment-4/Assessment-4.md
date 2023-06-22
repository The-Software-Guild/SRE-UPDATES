# Assessment: Deploy an API

## Overview
In this activity, you will launch the API you created in your k8s namespace. You will use all of the skills you learned in this course to modify the pipeline with the new API. If you are working in a group, each member of the group should take turns with the steps. 

A sample app is provided if you need a working app to deploy. If you wish to use the sample app, download and extract this zip file:

In this activity, you will only update the dev environment to test the new API. The provided API is a currency converter API. After deploying it, your team will add functionality to that API by creating new endpoints. The new endpoints will allow you to get quotes from crypto-currencies, and insert them into the orderbook application. You will add more endpoints later, but right now, let's focus on the deployment!

## Instructions

### Add Source Code to GitHub

1. Create a new branch for the [orderbook](https://github.com/The-Software-Guild/pss-orderbook-deploy) app, or use an existing branch that is part of the Jenkins pipeline.
    ```nocode
    git clone https://github.com/The-Software-Guild/pss-orderbook-deploy
    cd pss-orderbook-deploy
    git checkout -b <COHORT><TEAM>
    ```

2. Create a new folder in `src`, using the name of the API as the folder name. 
    ```nocode
    mkdir src/currencyAPI
    ```

3. Add the source code for the API to the new folder and then list the contents of the app to verify it worked. 
    ```nocode
    cp -r /path/to/app src/currencyAPI
    ls -l src/currencyAPI/app
    # __init__.py  main.py
    ```
    Make sure your app is in a directory named app and that there is has an empty `__init__.py` file along with a `main.py` file for the app. 

4. Create a `requirements.txt` file for the requred pip installs inside the source code folder.
    ```
    vi src/currencyAPI/requirements.txt
    ```

    Paste each of the app's dependencies in a new line of the file and save the file.

    ```nocode
    fastapi==0.95.1
    uvicorn==0.21.1
    requests==2.29.0
    SQLAlchemy==2.0.4
    pymysql==1.0.2
    cryptography==39.0.2
    ```

5. Create a dockerfile named Dockerfile_CurrencyAPI in `Dockerfiles`.
    ```nocode
    vi Dockerfiles/Dockerfile_currencyAPI
    ```

    Copy the docker instructions below and paste them into the new file.

    ```dockerfile
    FROM python:3.10.0
    WORKDIR /code
    COPY src/currencyAPI /code
    COPY src/currencyAPI/requirements.txt /code/requirements.txt 
    RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
    # uvicorn serves requests
    CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--workers", "2"]
    ```
6. Push to your branch. You may need to set the upstream origin if this is the first push. If so, follow the directions after `git push` in the standard output.

    ```nocode
    git status
    git add --all
    git commit -m"Adding currency API to branch "
    git push
    ```

### Update the Pipeline

1. Within your branch of the pss-orderbook-deploy repo, update the `Jenkinsfile` by adding another stage named for your API. You can do this by copying one of the other stages and then updating the stage name and kaniko command. Below is an example of the updated kaniko command with the new dockerfile and destination. 

    ```sh
    /kaniko/executor -f `pwd`/Dockerfiles/Dockerfile_currencyAPI -c `pwd` --insecure --skip-tls-verify --cache=false --destination=${ECR_REPO}:${JOB_NAME}currency-api-dev-${BUILD_NUMBER}
    ```
    A common error is curly brackets, make sure to follow the convention of the file.

2. Push your changes.

3. Log into [jenkins](https://jenkins.computerlab.online/) and locate your pipeline settings. Confirm that the pipelines branch matches the branch you used for your code changes and make appropriate updates if necessary.

4. Execute the pipeline and monitor for errors. Common errors are curly brackets in the Jenkinsfile or using the wrong naming convention. When you see the newly created image in the [ecr-list](http://ecrlist-ps.computerlab.online/index.php) with the name you used for the destination above, your delievery pipeline has been updated.

## Deploying to Dev

1. Change directory to the `sre-course-infra` repository.
    ```nocode
    cd /path/to/sre-course-infra
    ```
2. Change directory to your enviornment.
    ```nocode
    cd flux/apps/eks-sre-course/<COHORT>-<TEAM>-dev
    ```
3. Use or create a branch for your team
    ```nocode
    git checkout -b <COHORT><TEAM>-dev
    ```

4. Create three files to deploy this application.
    ```nocode
    touch deployment-currencyapi.yaml service-currencyapi.yaml imgPolicy-currencyapi.yaml
    ```
5. Copy the code provided by the devops team into these files. 

    - Copy contents of `deployment-dev-template.yaml` into `deployment-currencyapi.yaml`.
    - `service-dev-template.yaml` to `service-currencyapi.yaml`.
    - `imgPolicy-template.yaml` to `imgPolicy-currencyapi.yaml`.

6. Update the templates. Use `sed` to replace `<COHORT>`,`<TEAM>` and `<API>` with the correct values. For example 
    ```sh
    sed 's/<API>/currency/g' -i deployment-currencyapi.yaml service-currencyapi.yaml imgPolicy-currencyapi.yaml

    # sed on <COHORT>

    # sed on <TEAM>
    ```

7. Update the `ingress.yaml` file to make your service accessible over the Internet. Be sure to use your cohort and team number for `<COHORT>` and `<TEAM>`.
    - Under `spec: tls: -hosts:`, add a host for your new application. For example: `<COHORT><TEAM>dev-currencyapi.computerlab.online`
    - User `spec: rules:` Add a new host using the pattern below:
        ```nocode
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
    ```nocode
    git add service-currencyapi.yaml deployment-dev.yaml imgPolicy-currency.yaml ingress.yaml
    git commit -m "Adding a new service to dev"
    git push
    ```
9. Create a pull request and merge to the main branch. 

10. Test your app with the URL created in the ingress file and the `doc` endpoint such as `https://<COHORT><TEAM>dev-currencyapi.computerlab.online/docs`

### Troubleshooting
- Use the [k8s dashboard](https://k8sdashboard.computerlab.online/) to search for your namespace at the top and wait for the deployment to be available.
- Monitor the logs in [Grafana](https://grafana.computerlab.online/) for errors. Under the explore (compass icon) tab, you can select the `loki` data source and run the following queries to see the logs.

    For YAML errors
    ```nocode
    {job="flux-system/kustomize-controller"} |= `<COHORT>-<TEAM>-dev`
    ```

    For application errors
    ```nocode
    {namespace="<COHORT>-<TEAM>-dev", container="currencyapi"} |= ``
    ```

## Assignment

After launching the application, you will add endpoints to the new API to set up connections with the orderbook API. After doing so, prepare a 10-15 minute presentation explaining the changes you made.

- Go through the `app.py` file and implement each endpoint under the `# @CODE` comment.
- Each team member should code at least one endpoint.
- Verify that each endpoint in the file has a doc string that explains the endpoint and names the team member who implemented it.

To achieve a perfect mark you must implement all endpoints, account for errors, and present your work. The instructor will use the rubric below to grade your work.

## Rubric

The assessment will be marked out of 100. The table below describes the three different grading criteria and how to gain maximum points in each one.




| Deployment | Endpoints                      | Presentation |
| ---------- | ------------------------------- | ----------- |
| 50 points  | 30 points                      | 20 points    |
| - The team was able to deploy the API           | - Each team member completed at least one endpoint               | - Each team member participated in the presentation and talked about their contribution to the API deployment and endpoints |
| - The team was able to test and use the API           | - All endpoints are complete ( 6 points per endpoint )| - The presentation demonstrated an understanding of the code and pipeline          |
|    | - The code is well documented with doc strings | - The presentation included a demo of the API with explanation     |
