# automotive-market-analysis-system
Part of my Wrocław University of Science and Technology engineering thesis. The work focuses on a prototype system for collecting and analysing vehicle sales data.  
## Abstract
  The work focuses on the design and implementation of a prototype system for analyzing
data from vehicle sales advertisements obtained from selected online platforms. The primary
goal of the system is to automate the processes of collecting, analyzing, and visualizing
advertisement data. Additionally, the system has been enhanced with a feature for enriching
structured data using natural language processing (NLP) techniques. The system was designed
with a modular architecture that includes data extraction and analysis modules, a database, and
an interactive visualization interface. The study includes an analysis of existing solutions, such
as Otomoto, Omnipret, and Carfax, highlighting their limitations and areas for improvement.
Based on the conducted analyses, a system was designed and a prototype implemented,
enabling the analysis of vehicle sales history, an overview of car prices, and an examination of
general automotive market characteristics. The implementation utilized technologies such as
Python, Selenium, OpenAI, and Power BI, which enabled the creation of a prototype capable
of efficiently processing large datasets and generating detailed reports for various user groups.
The proposed solution provides users with advanced tools for easily analyzing the automotive
market, including aspects such as vehicle pricing, sales history, and overall market trends. The
work also identifies the potential for further development of the system, including full
deployment in a cloud environment and integration with additional data sources. The analysis
and implementation also pave the way for the development of a commercialized system of this
type.

## System structure
Achieving the set goal requires a modular system that allows for easily adding new modules and scaling the system according to current demands. This need is driven by the volume of data and the variability of its sources. Another critical aspect is the system's readiness to incorporate new data sources. The system comprises modules such as: the data collection and monitoring module, the extraction module, the data enrichment module, the database module, and the visualization module. These modules are interdependent, requiring proper sequencing in their operation and activation.

The data collection and monitoring module, responsible for gathering data without delving into individual sales listings, enables the identification of advertisements in the database and subsequent navigation to their pages. This module also divides the advertisements into batches sent to queues from which the next module retrieves them. By adjusting the number of queues, the rate of processed advertisements per minute can be controlled. The number of queues should correspond to the number of operational extraction modules.

The extraction module handles extracting detailed information from listing pages, such as vehicle parameters and other relevant details. This module also adds new records to the database. Isolating these tasks into a separate module enhances data extraction speed through duplication and simultaneous operation of multiple extraction modules.

The data enrichment module is responsible for cleaning and enriching data based on the description in the listing. This task is performed using selected NLP (Natural Language Processing) models and techniques, involving computational methods to represent, analyze, and generate natural language. This module operates independently and can be invoked anytime new data enters the system, regardless of the other modules' states.

The database module stores all system-related data. It connects with every other module in the system, making it a pivotal component.

The visualization module interacts directly with the end user. It summarizes the system's operations, presenting metrics, tables, and charts. Additionally, it provides user-friendly filtering and data searching capabilities within the database. This module must be fully adapted to user needs.

This modular system design significantly enhances scalability across various dimensions, including data collection and processing efficiency. It also allows for the seamless addition of new data sources with minimal modifications to the collection and extraction modules. The system architecture is illustrated in figure.  
<div align="center">
  <img src="https://github.com/user-attachments/assets/9952498a-5dc5-41d9-9079-16363c4b0fe8" alt="Opis obrazu">
</div>  

## Programming environments and tools used
A key part of the project implementation was the selection of appropriate development tools, particularly the programming language. Due to the broad scope of tasks to be accomplished, Python was chosen, as it offers a wide range of libraries suitable for building the entire system. Visual Studio Code was selected as the development environment due to its extensions that support work with cloud solutions and local servers.

For Web Scraping, the Selenium library was chosen. Selenium is a comprehensive tool designed to automate browser interactions realistically, enabling functionality to be tested as if performed by a user.

Another important library used in the system is Flask, a lightweight web framework that allows for the rapid development of web applications. Flask was utilized to create advertisement queues for the project.

For the data analysis module, the OpenAI Python package was used, offering a wide array of models and solutions specializing in text analysis, aligning well with the project's goals.

The pyODBC library was used to connect to the database, facilitating easy connections via the ODBC protocol. This solution streamlined the connection with Azure, which was employed for database creation and initially for the entire system's development.

For data visualization and the user interface, Power BI was used. It provides tools for visualizing and analyzing data intuitively, integrating information from various sources such as databases, files, folders, and web services.

These tools and environments enabled the creation of a complete system that meets the project objectives.

## interface

A prototype of the visualization module was created in Power BI, providing user-friendly and fully interactive reports. The reports follow a three-layered approach and the 3-30-300 rule to ensure clarity and usability. Each report uses carefully selected chart types and metrics to deliver the most valuable insights to users.

For visualizing general trends in the automotive market, the following elements were included:

- Top Section: Displays information about the sample size and the average listing duration. This helps users estimate the average sales time for vehicles with selected attributes.  
- Middle Section: Features three pie charts showing the percentage distribution of cars by color, fuel type, and seller type. For instance, analyzing the fuel type distribution offers insights into the progress of vehicle electrification in the country.  
- Bottom Section: Contains bar charts illustrating mileage distribution, the number of listings added on specific days of the week, and the most common vehicle origins.    
Sample views are shown in the figures below.  

<div align="center">
  <img src="https://github.com/user-attachments/assets/4f333730-61d3-4d9b-b351-f9e754cacda9" alt="Price analisis report.">  
  
  Price analisis report.  
</div>  
  
  
<div align="center">
  <img src="https://github.com/user-attachments/assets/9c2f1f2b-7e09-4189-8d75-1fc93b43db3f" alt="Price analisis report.">  

  Vehicle history report.  
</div>  
  
  
<div align="center">
  <img src="https://github.com/user-attachments/assets/54756b2e-c947-4133-b8ea-01e403457e8d" alt="Price analisis report.">  

  General market relationship analysis report.  
</div>  
