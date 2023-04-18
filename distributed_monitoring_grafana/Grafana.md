# Introduction to Dashboards

A Dashboard is a customizable data visualization tool. Dashboards are useful for grouping relevant metric-based visuals together. When building dashboards avoid overcomplicate them with repeat information. Use metrics that you suspect may relate to eachother (eg. volume, latency, and CPU usage).

In this activity, we will walk you through the creation of a basic dashboard. We will learn how to organize our dashboard with rows and folders. Finally, we will store a JSON backup of our dashboard, delete it and restore it as code.

**If more than one person per team is making a dashboard, please use your name instead of team**

## Step-by-Step: View Existing Dashboards

Before we create a dashboard, let's look at some pre-existing dashboards on our system.

1. Select the **FourSquare** Dashboards icon in the left-hand navigation bar.
   ![Grafana dashboard icon](https://the-software-guild.s3.amazonaws.com/sre/2207/images/GrafanaDashboardIcon.png)
2. Next, select **Browse**.
3. Locate the "Search for dashboards" textbox.
4. Search for each of the following dashboard titles.
   - `<COHORT><TEAM/NAME><ENV>` Dashboard
   - MySQL Orderbook
   - Jenkins
5. For each dashboard, observe the layout and types of monitoring visualizations used.

## Step-by-Step: Create a Dashboard

1. Hover over the Create icon
   ![Grafana Create Icon](https://the-software-guild.s3.amazonaws.com/sre/2207/images/GrafanaCreateIcon.png)

2. Select **New Dashboard** from the list to create an empty dashboard

3. Click the **Add a new panel** button in the **Add panel** box

4. On the right-hand side of the screen, locate **Title** under **Panel options** and change **Panel Title** to **Trade Volume**

5. At the top of this side of the screen, the graph type is currently **Time series**. Click on **Time series** and select **Pie chart**

6. Scroll down the right-hand side of the screen until you see **Legend**; click the button under **Visibility** to hide the legend.

7. Under the area where the graph will eventually appear, you'll see the **Query** section.

8. Make sure the **Data source** is **Prometheus**

9. In the **Metric** box, type in 
```
rate( # rate of trade request per second
    http_requests_total{
        handler=`/trade`
    }[$__rate_interval] # dynamic range
)
```


10. Select **Run Queries** to see the graph. Notice that you will see spikes when web traffic increases.

11. At the top of the screen change the time to **Last 1 hour**

12. Click the **Apply** button at the top left. This will return you to the dashboard with your new panel.

13. At this stage, you can resize the panel by grabbing the lower right corner and dragging

14. If you want to edit the panel further, click on the title `Stock Quote Volume` and select **Edit** to take you back into editing the panel.

15. To save your dashboard:

    - Click the Save Dashboard button at the top right of the screen
      ![Grafana Save Dashboard](https://the-software-guild.s3.amazonaws.com/sre/2207/images/GrafanaSaveDashboardIcon.png)

    - The first time you save the dashboard you will be required to provide a name. Use `<COHORT><TEAM/NAME><ENV> API Dashboard` as the name.

    - Click the save button

## Step-by-Step: Add Collapsible Rows

Rows allow you to create collapsible dashboards. For example, we may choose to put CPU and Memory usage in a row, then latency with volume in a subsequent row.


### Create a Collapsible Row

1. With the dashboard in view, click the Add New Panel button
   ![Grafana Add New Panel](https://the-software-guild.s3.amazonaws.com/sre/2207/images/GrafanaAddNewPanelIcon.png)
2. Click the Add New Row button
   ![Grafana Add New Row](https://the-software-guild.s3.amazonaws.com/sre/2207/images/GrafanaAddNewRowIcon.png)
3. This creates a new row with **Row title** as the title
4. Hover over **Row title** and a gear and trash can icon will appear
5. Click the **gear** icon
6. Type in **Volume** into the **Title** text area, overwriting the **Row title**
7. Click **Update**
8. Now drag your **Stock Quote Volume** panel into the row (if it is not already in the row).
9. To check that it is part of the row, click on the down arrow to the left of the **Volume** title. This will collapse the row and the panel will disappear.

You can add as many rows as you wish to separate out data in the dashboard.

## Step-by-Step: Folders

You will only need to create a folder if your instructor or someone else has not. The folder should be named based on your course `<COHORT><TEAM/NAME><ENV> API Dashboard`. Start back at the **Dashboard** home screen.

1. Select the **New** icon
   ![New button icon](https://the-software-guild.s3.amazonaws.com/sre/2210/images/new-button.png)
2. Click **Folder**
3. In the **Folder name** text box, type the name of your folder
4. Click **Create** button

A dashboard can be moved to a folder using these steps:

1. Hover over the Dashboard icon
   ![Grafana Dashboard Icon](https://the-software-guild.s3.amazonaws.com/sre/2207/images/GrafanaDashboardIcon.png)
2. Select **Browse**
3. Locate your dashboard name
4. Select the dashboard by clicking the **tick box**
5. Scroll back to the top of the screen and click the **Move** button
6. Select the folder that you wish to move your folder
7. Click the **Move** button

## JSON Backup

A JSON backup of a dashboard is handy because they can be shared, and even deployed as part of the pipeline. You will not be able to make new changes to this dashboard after completing this activity unless you update the JSON.

1. Examine the `stats.yaml` file in your Kubernetes prod folder. Our devops team configured our environment to use ConfigMap's to automate the deployment of dashboards. 

2. Go back to your dashboard, create a row for Contianer Metrics. Create two panels in this row. The first panel should be the rate of `container_memory_working_set_bytes` and the second a rate of a CPU metric. Refer to the "Distributed Monitoring System" activity if you need help under "More PromQL".

3. Apply your changes to the dashboard and save it.

4. Click on the settings gear of the dashboard, then click JSON Model. Have this JSON code ready to copy.

5. Within your local git repository and application folder, create a copy of the `stats.yaml` named `apidashboard.yaml`. Perform a code commit before modifying the file, so it is easy to track every change.

6. Edit the `apidashboard.yaml` file.
   - Edit the metadata name and json file name to something other than `<descriptitve_name>`. Commit the code when done.
      ```
      apiVersion: v1
      kind: ConfigMap
      metadata:
        name: <descriptive_name>
        namespace: prometheus
        labels:
          grafana_dashboard: "1"
      data:
        <descriptive_name>.json: |
      ``` 
   - Replace the json code with the code from your dashboard. YAML is indendation sensitive, the code you paste must be indented the same as the old code. 
   - Edit the GUID to a unique and random value.

7. Commit your recent changes and create a pull request. Within 5 minutes of merging the dashboard should appear in Grafana. If you do not see your dashboard after 5 mintutes look at the checkout history of the file in the github website, see if the indendation was modified between commits. Use the query below to see if any errors are in your YAML. 
    ```
    {job="flux-system/kustomize-controller"} |= `<COHORT>-<TEAM>-<ENV>`
    ```

## Conclusion

Dashboards are a key element to ensuring a visual understanding of what is happening in our environment. A good dashboard layout helps everyone on the team understand where the initial problem is, and we should design our dashboards with simplicity at the top, with the ability to drill down into deeper layers to the root cause of a problem.