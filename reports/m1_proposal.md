# Maple Eagle Trade Tracker Proposal

> Milestone 1  
> Group 13  
> Authors: Sopuruchi Chisom, Bryan Lee, Alex Wong, Yun Zhou  
> [Project Github Repo](https://github.com/UBC-MDS/DSCI-532_2025_13_Maple-Eagle-Trade-Tracker)

## Motivation and Purpose
**Our Role**  
We are freelance **data scientists** contracted by  **Government of Canada** to develop data-driven solutions for economic challenges arising from international trade disputes.

**The Audience**  
Our primary audience is Canadian government agencies, such as **Department of Finance Canada** and **Export Development Canada**, which are responsible for formulating policies in response to the economic impacts of the 2025 tariff disputes between Canada and the United States.

**The Problem**  
In light of the 2025 *tariff wars* between Canada and the United States, the Canadian government faces the challenge of understanding the economic impact of import and export bans on various sectors. This is particularly important as it impacts several key sectors and geographical areas, resulting in strains to businesses and consumers alike.

**Our Solution**  
We propose a dashboard that provides clear, interactive visualizations of the sectors and geographical areas most affected by the tariff bans. By identifying which industries are under the most strain and pinpointing the regions experiencing the highest levels of economic disruption, the dashboard will empower government agencies to make informed decisions. This, in turn, can help alleviate the economic burden on citizens by guiding the government in diversifying its support for the affected sectors.

## Question 2 : Description of the data (Robbie)
Include how many rows and columns there are in the dataset (that you plan to use).
There should be a clear link to how the dataset and the variables you describe will help you solve your target audience's problem.
Indicate at least one new variable that you are planning to derive/engineer for your visualizations.
If there are no new variables to derive, indicate what additional information you would have liked to have in the dataset to better be able to answer your research questions (even if it is impossible for you to engineer it).
If you are planning to visualize a lot of columns, provide a high level description of the variable types rather than listing every single column.
For example, indicate that the dataset contains a variety of categorical variables for demographics and provide a brief list rather than describing every single variable.
You may also want to consider visualizing a smaller set of variables given the short duration of this project.

## Question 3: Research questions and usage scenarios (Alex)
The purpose of this section is to get you to think in more detail about how your target audience will use the app you're designing and to account for these detailed needs in the proposal.
For this it can be helpful to create a brief persona description of a member in your intended target audience
Then, think about what they might want to do with your app and write small user story. User stories are typically written in a narrative style and include:
The specific context/background of the user
The overall goal of the user
Tasks needed to reach that goal
A hypothetical walkthrough of how the user would accomplish those tasks with your app
The outcome/action that the user would take based on the information they find in the app


## Question 4: App Sketch & Brief Description

![Dashboard Sketch](../img/sketch.png)

This dashboard provides a comprehensive view of Canada's trade metrics for 2024, focusing on total imports and exports in CAD. Key performance indicators (KPIs card figure 1 and 2) for imports and exports, representing the most recent year, are displayed at the top of the dashboard. A line chart to the right (figure 3) shows trade balance volume over the past decade, indicating whether Canada had a trade surplus or deficit each year based on the difference between imports and exports. In the center, an interactive map (figure 6) visualizes trade balance by province, with provinces color-coded from green to red, based on their trade balance (imports minus exports). The two splicers (figure 7 and 8) allow for filtering by trade sector (e.g., fishing, agriculture, mining) and by province/territory, dynamically updating the entire dashboard. On the left, two vertical bar charts (figure 4 and 5) display the total import and export volumes, while two additional bar charts at the bottom (figure 9 and 10) show annual import and export values in CAD from 2014 to 2024. The provincial map updates based on the selected province, and the sector bar chart adjusts to display data for the selected trade sector by reducing the number of bars selected. All visualizations are linked to the two splicers, offering a tailored view of Canada's trade landscape.