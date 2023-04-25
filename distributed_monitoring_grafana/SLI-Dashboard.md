# SLI Dashboard

It is time to build a dashboard for monitroing the reliability of the site. If you have not completed the "Introduction to Dashboard" activity, please complete that one before attempting this activity. You can build one dashboard as a group named `<COHORT><TEAM><ENV>`, or build one with your name instead of team. As you go through this activity, try out different visualization types and settings.

The headings below are rows (Logs, Latency, Availability, Container Metrics, Volume). Each row has panels that you will create in your dashboard. The last activity is to add an alert to a panel.

## Logs
Start by making a row for logs. It is important to always have fast access to logs when trouble shooting. If you need help refer to `Distributed Monitoring Systems, Section 'Loki Introduction' `

### Panels

1. Namespace Logs - display your namespace log stream from Loki. make sure to change the visualation in the edit panel page to logs.

2. GitOPS (FluxCD) logs - Apply a line filter for your namespace. 

## Latency

Adding a background color for regions that are in breach of our SLI will make it . For the latency panels, you can modify the time series charts by following these steps:    
- Change "Show Threshold" to "As Filled Regions"
- Make the base color red
- Add a orange threshold set at 85
- Add a green threshold at 95

### Panels

1. Percentage of all request le 500 milliseconds - if you need help see `Distributed Monitring Systems 'Latency Example'`

2. Percentage of all request faster than 500 miliseconds by handler (endpoint) - Refer to `Distributed Monitring Systems 'Aggregations'`

3. Percentage of Trade request le 750 milliseconds - You should be able to use number 1 above, just add a label or line filter for '/trade'

## Availability

Make sure to select the appropriate visualizations when building your panels. 

### Panels:

1. MySQL Up - Status of availability of MySQL. For help see `Distributed Monitring Systems 'More PromQL'`

2. Jenkins Health Score - Create a panel to display if Jenkins is up. Use `jenkins_health_check_score`

3. Num of Replicas per Deployment - Use the `sum by` on the `deployment` label to have this stat for each deployment. For help see `Distributed Monitring Systems 'More PromQL' and 'aggregations'`

4. All 2xx Request / Errors (not 4xx) - Add a `sum by` on handler. See `Distributed Monitring Systems 'Prometheus step 6' and 'aggregations'`. Add some color to the visual so that it is easy to see when this percentage goes below 95%. Set a Max under Standard Option to 101 and minimum to 70.

5. Site Probe Status - Examine `probe.yaml`. This probe resource is constantly checking if our site is up and the metric is available in prometheus through `probe_success{job="blackbox",namespace="<COHORT>-<TEAM>-<ENV>"}.` Modify the chart so that it is easy to see when the probe fails.

6. Percentage of Client Errors - Use the `http_requests_total` metric to calculate what percentage of request are 4xx. This is similar to number 4 above.


## Container Metrics

See `Distributed Monitring Systems 'More PromQL'`.  

For both queries below:  
- Use a `sum by` on container. 
- Add a regulat expression to search for all containers matching this pattern `'orderbook.*'`

### Panels: 

1. CPU Usage By Deployment Rate - Use `sum by` on deployment.

2. Memory Usage By Deployment Rate - Use `sum by` on deployment.

## Volume

### Panels:

1. Number of Requests  / Endpoint / Minute - `Distributed Monitring Systems 'Aggregations'`.  

2. Number of MySQL Connections - Use `mysql_global_status_threads_connected`

3. Number of Successful Jenksins Builds - Use `default_jenkins_builds_success_build_count_total`. Invistigate the label you need to filter on.

4. Percentage of Jenkin Builds Success Vs Fail - Use `default_jenkins_builds_success_build_count_total` and `default_jenkins_builds_fail_build_count_total`. Try different features of the panel, like a pie chart from two queries.

---

## Add an Alert

Too many client errors, such as 404 request, suggest that our clients are experiencing errors when using our website. We will add an alert to our dashboard that will notify our team when more than 15% of web request are client erros. Our SLA requires trades to execute in under a second, we will create an alert for our SLI of trade request being faster than 750 miliseconds. 

These are the two panesl we will add alerts too.  
- Percent of Trade requests le 750 miliseconds
- Percent of Client Errors

To add an alert follow these steps:

1. Click on edit for one of the panels.
2. Click on the Alert tab. Create alert rule from this panel.
3. Make sure Grafana Managed Alert is selected. Change the time frame near loki to `now-5 mins to now`. 
4. Scroll down the the box labeled 'B' and change the function to `SUM`.  
5. In Box 'C' change the threshold to :  
    - For Percent of Trade Requests le 750 milliseconds use "Is Below" and 95.
    - For Percent of Client Erros use "Is Above" and 15
6. Make sure the alert is set to evalualte every 1m for 5 minutes. This will make the alert wait 5 minutes in pending before firing off.
7. Select your folder, and use your team name for group. 
8. Save and exit. Then repeat if you have not done both alerts. You will notice that the panels now have a green heart in the dashboard. They will change color depending on the status of the alert. 

When you have completed both alerts, test them. Spam this URI for 5 minutes to create too many 404 requests `https://c500team01prod-api.computerlab.online/nofile`, and monitor your alert in the dashboard or on the alert page in Grafana. You can try to do the same for the trade SLI by executing a lot of trades.

## Bonus

Add this as a panel below:

### Avg Milliseconds / Endpoint / Minute
```
avg(avg_over_time({app="ingress-nginx"} 
    !="/metric" 
    | json
        # remove json parsing errors  
      |  __error__!=`JSONParserErr` 
      | host =`<COHORT><TEAM><ENV>-api.computerlab.online`
      # successfull request 
      | upstream_status=~"(2|3)[0-9]{2}"
      # create a field named path to group by  
      | regexp `request_uri["\s:]+(?P<path>[\/]+[a-z_]+).*` # create field named path
      # The unwrap allows us to specify the field and time range for our average
      | unwrap upstream_response_time[1m])
 ) by (path) * 1000
 
```

## Solution

The yaml file sli-dashboard contains the dashboard for this activity. Run the command below replacing <COHORT>, <TEAM> and <ENV> with your correct values.
```
sed 's/c500/<COHORT>/g;s/team01/<TEAM>/g;s/prod/<ENV>/g' SLI-DashboardSolution.yaml -> sli-dashboard.yaml
```

Then upload the sli-dashboard.yaml file to your applications deployment folder. This will create the dashboard for you. Please inspect the queries that you struggled with in the solution. Note that the dashoard from the sli-dashboard.yaml will not have alerts.
