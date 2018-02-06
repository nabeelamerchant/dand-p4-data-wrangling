# dand-p4-data-wrangling
Data Wrangling project using OpenStreetMap from Udacity's Data Analyst Nanodegree

<h4>Toronto Open Street Maps Data</h4>

For this project I will be analyzing the Open Street Maps data pertaining to the city of Toronto in Canada.

The original OSM XML file was exported from Overpass API using the following coordinates as the bounding area: -79.6694 to -79.0891 and 43.5635 to 43.8736.

In order to translate the xml file into a database, I first needed to take a look at the different nodes, node tags, etc. to get a better sense of the data and see if anything needed to be fixed.

<h4>Auditing the data</h4>

I then audited the sample file to search for inconsistencies in the street names, postal codes, and city names. This was an iterative process that involved identifying the different groups of street name endings, types of postal code recordings, and city names, and then creating a list of acceptable types to filter out any inconsistencies.

These lists were then used later on with the original xml file to identify further inconsistencies and determine what changes needed to be made. The code for this can be found in "3. audit_addresses.py".

<h4>Cleaning the data</h4>

Once these errors were identified, I used the script "4. update_osm.py" to go through the xml file and make changes to fix the errors, mainly using dictionaries to map the incorrect entities to the correct ones. The corrections were then written to a new xml file. This had to be repeated a few times to catch stacked errors.

Examples of the types of errors and how they were treated can be found in the Project 4 pdf.

<h4>Converting XML to CSV</h4>

Once I was happy with the updated xml file, I used the script "5. convert_osm_to_csv.py" to convert the updated xml file to individual csv files for each table based on the schema provided. This resulted in 5 separate csv files that I could then import into the database. 

<h4>Database Creation</h4>

To create the database 'Toronto.db', I used sqlite3 in the command line to create the tables according to the schema provided and import the csv files. The commands used are listed in the text file 'sqlite3_commands.txt'.

<h4>Querying the Database</h4>

Now that the data was audited and imported, I could query it to find some interesting information about the city of Toronto. Some examples of things queried were as follow. More examples can be found in the Project 4 pdf.

- Top 10 amenities in Toronto:

  - restaurant,2072
  - fast_food,2010
  - bench,1612
  - post_box,1389
  - cafe,1073
  - parking,947
  - waste_basket,867
  - bank,706
  - pharmacy,498
  - telephone,494
  
(select value, count(value) from nodes_tags where key='amenity' group by
value order by count(value) desc limit 10;)

- Top 5 most popular coffee shops (restaurants):

  - "Tim Hortons",235
  - "Starbucks Coffee",170
  - "Second Cup",71
  - "Country Style",16
  - "Coffee Time",8

(create view coffee_id as select id from nodes_tags as coffee_id where
value="coffee_shop";
select nodes_tags.value,count(nodes_tags.value) from
coffee_id,nodes_tags where coffee_id.id=nodes_tags.id and
nodes_tags.key='name' group by nodes_tags.value order by
count(nodes_tags.value) desc limit 5;)

Note that the database isn't present as it's too large to host.
