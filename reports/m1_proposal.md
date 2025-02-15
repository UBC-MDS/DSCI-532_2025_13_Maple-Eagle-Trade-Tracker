---
editor_options: 
  markdown: 
    wrap: sentence
---

# Maple Eagle Trade Tracker Proposal

> Milestone 1\
> Group 13\
> Authors: Sopuruchi Chisom, Bryan Lee, Alex Wong, Yun Zhou\
> [Project Github Repo](https://github.com/UBC-MDS/DSCI-532_2025_13_Maple-Eagle-Trade-Tracker)

## Motivation and Purpose

**Our Role**\
We are freelance **data scientists** contracted by **Government of Canada** to develop data-driven solutions for economic challenges arising from international trade disputes.

**The Audience**\
Our primary audience is Canadian government agencies, such as **Department of Finance Canada** and **Export Development Canada**, which are responsible for formulating policies in response to the economic impacts of the 2025 tariff disputes between Canada and the United States.

**The Problem**\
In light of the 2025 *tariff wars* between Canada and the United States, the Canadian government faces the challenge of understanding the economic impact of import and export bans on various sectors.
This is particularly important as it impacts several key sectors and geographical areas, resulting in strains to businesses and consumers alike.

**Our Solution**\
We propose a dashboard that provides clear, interactive visualizations of the sectors and geographical areas most affected by the tariff bans.
By identifying which industries are under the most strain and pinpointing the regions experiencing the highest levels of economic disruption, the dashboard will empower government agencies to make informed decisions.
This, in turn, can help alleviate the economic burden on citizens by guiding the government in diversifying its support for the affected sectors.

## Question 2 : Description of the data (Robbie)

Include how many rows and columns there are in the dataset (that you plan to use).
There should be a clear link to how the dataset and the variables you describe will help you solve your target audience's problem.
Indicate at least one new variable that you are planning to derive/engineer for your visualizations.
If there are no new variables to derive, indicate what additional information you would have liked to have in the dataset to better be able to answer your research questions (even if it is impossible for you to engineer it).
If you are planning to visualize a lot of columns, provide a high level description of the variable types rather than listing every single column.
For example, indicate that the dataset contains a variety of categorical variables for demographics and provide a brief list rather than describing every single variable.
You may also want to consider visualizing a smaller set of variables given the short duration of this project.

## Question 3: Research questions and usage scenarios (Alex)

Dominic is a senior trade policy analyst at the Department of Finance Canada and his primary role is to monitor trade flows between Canada and its trading partners and provide policy recommendations that benefit Canada.

In light of the tariff threats from the new US administration, Dominic wishes to assess the economic impact of the proposed US tariffs and how can Canada retaliate effectively.

Particularly, Dominic need to understand:

1.  The approximate dollar amount of Canadian exports subjected to US tariffs;
2.  Which sectors / industries are hit the hardest;
3.  Which provinces are being impacted the most by the tariffs;
4.  What do Canada import the most from the US.

When Dominic opens the Maple-Eagle Trade Tracker, he will see bar charts that visualizes Canada's export to US, and Canada's import from the US broken down by sector.
Through the option bars on the side Dominic can also filter for sectors of interest and the selected sectors will be broken down further to sub-categories.
The tracker also provides a map that displays import/export data for each province and time series trade data with the US.

Through the use of the Tracker, Dominic discovers BC will be one of the hardest hit provinces by the US tariffs due to the large volume of lumber exported to the US.
He also noticed BC's lumber exports to the US has been steadily rising in recent years and have decided to place BC's lumber industry as priority for the new subsidy program prepared by the Department of Finance.
On the other hand, Dominic learned alcoholic beverages is a key import from the US and so Dominic advises the Department of Finance to explore ways to help the Canadian hospitality industry diversify their supply network for alcoholic beverages while proposing retaliatory tariffs on US alcohol.

## Question 4: App sketch & brief description (Bryan)

![Dashboard Sketch](../img/sketch.png)

This dashboard provides a comprehensive view of Canada's trade metrics for 2024, focusing on total imports and exports in CAD.
Key performance indicators (KPIs card figure 1 and 2) for imports and exports, representing the most recent year, are displayed at the top of the dashboard.
A line chart to the right (figure 3) shows net trade volume over the past decade, indicating whether Canada had a trade surplus or deficit each year based on the difference between imports and exports.
In the center, an interactive map (figure 6) visualizes net trade by province, with provinces color-coded from green to red, based on their trade balance (imports minus exports).
The two splicers (figure 7 and 8) allow for filtering by trade sector (e.g., fishing, agriculture, mining) and by province/territory, dynamically updating the entire dashboard.
On the left, two vertical bar charts (figure 4 and 5) display the total import and export volumes, while two additional bar charts at the bottom (figure 9 and 10) show annual import and export values in CAD from 2014 to 2024.
The provincial map updates based on the selected province, and the sector bar chart adjusts to display data for the selected trade sector by reducing the number of bars selected.
All visualizations are linked to the two splicers, offering a tailored view of Canada's trade landscape.
