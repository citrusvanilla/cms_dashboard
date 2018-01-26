# An Example Dashboard and Time-Series Analysis for a CMS Database

This is an example of a Dash interactive Python framework developed by [Plotly](https://plot.ly/).

The app is deployed on Heroku and can be accessed [here](https://citrusvanilla-cms-dashboard.herokuapp.com/).

This app fetches a CSV of historical contacts from a local CSV file. All parameters of the dashboard are adjustable. An accompanying time-series analysis in the file ts_analysis.ipynb demonstrates a decomposition of the data into seasonal and trend elements.  This analysis allows us to use a simple cross-month ordinary least squares regression to make a short term, 1-year forecast for aggregate client contacts.

The following is a screenshot for the app in this repo:

![Alt desc](https://i.imgur.com/iOHI9yO.jpg)
