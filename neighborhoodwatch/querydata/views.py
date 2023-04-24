from django.http import HttpResponse
from django.template import loader
import base64
import getpass
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np;
import oracledb

pw = getpass.getpass("Enter password: ")

connection = oracledb.connect(
    user="esteban.medero",
    password=pw,
    dsn="oracle.cise.ufl.edu:1521/orcl")

print("Successfully connected to Oracle Database")

#initial query page provides users the opportunity to select from which states they would
#like to pull statistics from
def index(request):

    #initialize cursor to connect to database
    cursor = connection.cursor()

    #queries initial options to select states
    cursor.execute("SELECT distinct statename FROM agency")
    res = cursor.fetchall()

    #create a list to store column names from current query to post at top of table
    columnnames = []
    for item in cursor.description:
        columnnames.append(item[0])

    #creates a list to pass in state names for options list
    states = []
    for items in res:
        states.append(items[0])

    #queries second field to select distinct agency types
    cursor.execute("SELECT distinct agencytype FROM agency")
    temp = cursor.fetchall()

    #creates a list to store optional agency types
    agencytypes = []
    for items in temp:
        agencytypes.append(items[0])

    #Load the necessary HTML templated to render data on
    template = loader.get_template("querydata/index.html")

    #pass along contextual items to display data in the template
    context = {
        "query" : res,
        "columns" : columnnames,
        "states" : states,
        "agencytypes" : agencytypes
    }

    #respond
    return HttpResponse(template.render(context, request))

#Second webpage view offers users the opportunity to select their desired location within
#the states they had previously selected
def agencySelection(request):

        #initialize cursor to connect to database
        cursor = connection.cursor()

        #take in all of the form selection from the state selection page and format them for 
        #a valid SQL query
        selectedStates = request.POST.getlist('selection')
        selectAgencyType = request.POST.getlist('typeAgency')
        selectedYears = request.POST.getlist('year')
        stateQuery = '\' OR statename = \''.join(selectedStates)
        typeQuery = '\' OR agencytype = \''.join(selectAgencyType)
        yearQuery = '\' OR year = \''.join(selectedYears)

        #initial query pulls the table results to display on the next page
        #checks if a previous query view exists in the data base if so removes it
        cursor.execute("SELECT view_name FROM user_views")
        checkViews = cursor.fetchall()
        for columns in checkViews:
            for views in columns:
                if views == 'AVAILABLEAGENCIES':
                    cursor.execute("DROP VIEW availableagencies")
                if views == 'AGENCIESID':
                    cursor.execute("DROP VIEW agenciesid")
          
        #adds the query view for the current session and displays all items available
        #creates separate view with respective agencyid for later querying
        cursor.execute("CREATE VIEW agenciesid AS SELECT distinct agencyid, statename, agencyname, year FROM agency WHERE (statename = \'" + stateQuery + "\') AND (agencytype = \'" + typeQuery + "\') AND (year = \'" + yearQuery + "\')") 
        cursor.execute("CREATE VIEW availableagencies AS SELECT distinct statename, agencyname, agencytype FROM agency WHERE (statename = \'" + stateQuery + "\') AND (agencytype = \'" + typeQuery + "\')")
        cursor.execute("SELECT * FROM availableagencies")
        res = cursor.fetchall()

        #create a list to store column names from current query to post at top of table
        columnnames = []
        for item in cursor.description:
            columnnames.append(item[0])

        #creatse a list to store names of specific agencies
        agencynames = []
        for items in res:
            agencynames.append(items[1])

        #Load the necessary HTML templated to render data on
        template = loader.get_template("querydata/index.html")
        numberStates = len(selectedStates)

        #pass along contextual items to display data in the template
        context = {
            "query" : res,
            "columns" : columnnames,
            "agencynames" : agencynames,
            "selectedStates" : selectedStates,
            "selectAgencyType" : selectAgencyType,
            "selectedYears" : selectedYears,
            "numberStates" : numberStates
        }

        #respond 
        return HttpResponse(template.render(context, request))

def parameterSelection(request):

    #initialize cursor to connect to database
    cursor = connection.cursor()

    selectedAgencies = request.POST.getlist('nameAgency')
    selectAgencyType = request.POST.getlist('agencyType')
    selectedStates = request.POST.getlist('state')
    selectedCrimeFamily = request.POST.getlist ('crimeFamily')
    selectedYears = request.POST.getlist('year')
    selectedGraph = request.POST.get('graph')
    filteredCrimes = request.POST.getlist('crime')

    crimeFamilyQuery = ""
    #builds a query to union all selected parent tables for their repsective crime family
    #and extracts their unique crimeID
    for family in selectedCrimeFamily:
        if family == selectedCrimeFamily[len(selectedCrimeFamily) - 1]:
            crimeFamilyQuery = crimeFamilyQuery + " SELECT distinct CRIMEID FROM " + family
        else:
            crimeFamilyQuery = crimeFamilyQuery + " SELECT distinct CRIMEID FROM " + family + " UNION"

    #checks if the updated family ID view is in the session yet
    #if so removes it and recreates it with the necessary values
    cursor.execute("SELECT view_name FROM user_views")
    checkViews = cursor.fetchall()
    for columns in checkViews:
        for views in columns:
            if views == 'FAMILYIDS':
                cursor.execute("DROP VIEW familyids")

    #create view with desired crime family ID values
    cursor.execute("CREATE VIEW familyids AS" + crimeFamilyQuery)
    cursor.execute("SELECT * FROM familyids")
    familyIDS = cursor.fetchall()
    
    #prepares necessary string to join necessary 
    allCrimeTables = ["assault", "drugnarcotic", "fraud", "gambling", "homicide", "humantrafficking", "otherproperty", "othersociety", "prostitution", "sexoffense", "theft"]
    updatedCrimeTable = []

    #iterate over each table with name from allCrimeTables and find if they share a respective crimeID 
    #with users selection if so add them to the updated list
    for crimeTypes in allCrimeTables:
        cursor.execute("SELECT distinct CRIMEID FROM " + crimeTypes)
        checkID = cursor.fetchall()
        for columns in checkID:
            for cID in columns:
                for col in familyIDS:
                    for fID in col:
                        if cID == fID:
                            updatedCrimeTable.append(crimeTypes)

    #checks to see if previously updated views are in the database
    cursor.execute("SELECT view_name FROM user_views")
    checkViews = cursor.fetchall()
    for crimes in allCrimeTables:
        crimeToCheck = "updated" + crimes
        for columns in checkViews:
            for views in columns:
                if crimeToCheck.upper() == views:
                    cursor.execute("DROP VIEW " + crimeToCheck)

    updatedViewTables = []

    #creates new views for each crime table that matches selected
    # crimeID without the crimeID column
    for crimes in updatedCrimeTable:
        newViewName = "updated" + crimes
        newView = "CREATE VIEW " + newViewName + " AS SELECT "
        cursor.execute("SELECT * FROM " + crimes)
        for col in cursor.description:
            if col[0] == 'CRIMEID':
                continue
            else:
                if col[0] == cursor.description[len(cursor.description) - 1][0]:
                    newView = newView + col[0]
                else:
                    newView = newView + col[0] + ", "
        newView = newView + " FROM " + crimes
        updatedViewTables.append(newViewName)
        cursor.execute(newView)

        print(updatedCrimeTable)
    
    #builds query to compile the final table view that comprises of all items joined together
    combinedView = ""
    for views in updatedViewTables:
        if views == updatedViewTables[0]:
            combinedView = views + " LEFT JOIN "
        elif views == updatedViewTables[len(updatedViewTables) - 1]:
            combinedView = combinedView + views + " using (CRIMESID)"
        else:
            combinedView = combinedView + views + " using (CRIMESID) LEFT JOIN "

    #Checks to see if the final crime table view exists from a previous iteration
    #or if final agencies view exists
    cursor.execute("SELECT view_name FROM user_views")
    checkViews = cursor.fetchall()
    for columns in checkViews:
        for views in columns:
            if views == 'FINALCRIMETABLE':
                cursor.execute("DROP VIEW FINALCRIMETABLE")
            if views == 'FINALAGENCIES':
                cursor.execute("DROP VIEW FINALAGENCIES")

    agencies = "\' OR agenciesid.agencyname = \'".join(selectedAgencies)
    #final agencies table
    print("CREATE VIEW finalagencies AS SELECT * FROM agenciesid WHERE agenciesid.agencyname = \'" + agencies + "\'")
    # cursor.execute("CREATE VIEW finalagencies AS SELECT * FROM agenciesid WHERE agenciesid.agencyname = \'" + agencies + "\'")
    # cursor.execute("CREATE VIEW finalcrimetable AS SELECT distinct * FROM " + combinedView)


    # cursor.execute("SELECT distinct * FROM finalagencies INNER JOIN finalcrimetable ON finalagencies.agencyid = finalcrimetable.crimesid")
    # table = cursor.fetchall()
    
    # columnnames = []
    # for item in cursor.description:
    #     columnnames.append(item[0])

    template = loader.get_template("querydata/index.html")

    finalQuery = True

    ########################### GRAPHICS SECTION JEREMY INTEGRATION#################################

    # Formulate Crime Query
    crimeQuery = "SUM(" 
    for crime in filteredCrimes:
        crimeQuery += (crime + ") AS " + crime + ", SUM(")
    crimeQuery = crimeQuery[0:-4] # Remove Extra "SUM("

    #Formulate SQL Query
    command = ("SELECT c.year AS Year,"
        + ("""
            SUM(simpleAssaults) + SUM(aggravatedAssaults) + SUM(intimidations) + SUM(murders) + 
            SUM(justifiableHomicides) + SUM(negligentMansalughters) + SUM(commercialSexActs) + 
            SUM(involuntaryServitudes) + SUM(kidnappings) + SUM(rapes) + SUM(sodomies) + 
            SUM(sexualAssaultsObject) + SUM(fondlings) + SUM(incests) + SUM(statutoryRapes) crimes_against_persons,
        """ if ("CRIMESAGAINSTPERSONS" in selectedCrimeFamily) else "")
        + ("""
            SUM(swindles) + SUM(welfareFrauds) + SUM(wireFrauds) + SUM(impersonations) + 
            SUM(identityThefts) + SUM(creditCardFrauds) + SUM(hackings) + SUM(pickpocketings) + 
            SUM(purseSnatchings) + SUM(shopliftings) + SUM(buildingThefts) + SUM(vehicleItemThefts) + 
            SUM(vehiclePartThefts) + SUM(coinOperatedDeviceThefts) + SUM(otherThefts) + 
            SUM(arsons) + SUM(briberies) + SUM(counterfeitsForgeries) + SUM(embezzlements) + 
            SUM(extortions) + SUM(vehicleThefts) + SUM(robberies) + SUM(stolenProperty) + 
            SUM(burglariesBreakingEnterings) + SUM(destructionDamageVandalismProperty) crimes_against_property,
        """ if ("CRIMESAGAINSTPROPERTY" in selectedCrimeFamily) else "")
        + ("""
            SUM(drugNarcoticOffenses) + SUM(drugNarcoticViolations) + SUM(drugEquipmentViolations) + 
            SUM(bettings) + SUM(sportsTamperings) + SUM(gamblingEquipmentViolations) + 
            SUM(operatingPromotingAssistingGamblings) + SUM(prostitutions) + SUM(purchasedProstitutions) + 
            SUM(assistingPromotingProstitutions) + SUM(animalCruelties) + SUM(pornographyObsceneMaterials) + 
            SUM(weaponLawViolations) crimes_against_society,
        """ if ("CRIMESAGAINSTSOCIETY" in selectedCrimeFamily) else "")

        + crimeQuery

        + """
            agencyname
        FROM crimes c
        JOIN assault ON c.crimesid = assault.crimesid
        JOIN fraud ON c.crimesid = fraud.crimesid
        JOIN gambling ON c.crimesid = gambling.crimesid
        JOIN homicide ON c.crimesid = homicide.crimesid
        JOIN humantrafficking ON c.crimesid = humantrafficking.crimesid
        JOIN otherproperty ON c.crimesid = otherproperty.crimesid --(Fixed) Only 2016 & 2019 for some reason?
        JOIN othersociety ON c.crimesid = othersociety.crimesid
        JOIN prostitution ON c.crimesid = prostitution.crimesid
        JOIN sexoffense ON c.crimesid = sexoffense.crimesid
        JOIN theft ON c.crimesid = theft.crimesid
        JOIN drugnarcotic ON c.crimesid = drugnarcotic.crimesid
        JOIN agency ON c.agencyid = agency.agencyid
        """ 

    + (("WHERE c.year = " + selectedYears[0]) if (len(selectedYears) == 1)
        else ("WHERE (c.year = " + (" OR c.year = ".join(selectedYears))) + ")")

    + " AND agencyname = '" + ("' OR agencyname = '".join(selectedAgencies) + "'")

    + """
    GROUP BY agencyname, c.year
    ORDER BY c.year ASC, agencyname DESC
    """)

    print(command) # For Debug

    # Execute SQL Command and Get Results
    cursor.execute(command)
    res = cursor.fetchall()

    #create a list to store column names from current query to post at top of table
    columnnames = []
    for item in cursor.description:
        columnnames.append(item[0])

    #create a list to store column names from current query to post at top of table
    columns = []
    for item in cursor.description:
        columns.append(item[0])

    # Create Global Figure Object, We Will Later Pass this to The Template
    fig = plt.figure()

    if (selectedGraph == "Line"):

        values  = []
        years  = []

        # Create List The Correct Size
        for _ in range(len(columns) - 2):
            values.append([])

        # Construct a 2d Array Of All Selected Crimes, stored by [Crime Type, Year]
        for item in res:
            if (item[0] in years):
                for i in range(len(item)):
                    if (i != 0 and i != (len(item) - 1)):
                        values[i - 1][years.index(item[0])] += item[i]
            else:
                years.append(item[0])
                for i in range(len(item)):
                    if (i != 0 and i != (len(item) - 1)):
                        values[i - 1].append(item[i])
        # Create Plot, plot() is the lines, scatter() is the points 
        for i in range(len(values)):
            plt.plot(years, values[i], label = columns[i + 1])
            plt.scatter(years, values[i])

        # Fixes Weird X-Axis Distribution On This Graph Type
        fig.axes[0].xaxis.set_ticks(years)

        # This graph works fine with multiple agencies selected so this just changes the title to match that
        if (len(selectedAgencies) == 1):
            plt.title("Total Crimes per Year in " + res[0][len(res[0]) - 1]) # Ugly Statement is just getting the Agency name
        else:
            plt.title("Total Crimes per Year in Agencies")
        plt.legend()

    elif (selectedGraph == "Bar"):
        values  = []
        agencies = []

        # Create List The Correct Size
        for _ in range(len(columns) - 2):
            values.append([])

        # Construct a 2d Array Of All Selected Crimes, stored by [Crime Type, Agency]
        for item in res:
            if (item[-1] in agencies):
                for i in range(len(item)):
                    if (i != 0 and i != (len(item) - 1)):
                        values[i - 1][agencies.index(item[-1])] += item[i]
            else:
                agencies.append(item[-1])
                #tempList = []
                for i in range(len(item)):
                    if (i != 0 and i != (len(item) - 1)):
                        values[i - 1].append(item[i])

        # Empty Arrary For Stacked Barplot
        bottom = np.zeros(len(agencies))

        # Workaround For Stacked bar Plot, Draws Several Bat Plots At Staggered Heights, Seems To Work Well
        for i in range(len(columns) - 2):
            plt.bar(agencies, values[i], 0.5, label=columns[i + 1], bottom=bottom)
            bottom += values[i]

        plt.title("Crime Distributions Per County")
        plt.legend()

    elif (selectedGraph == "Pie"):
        values  = []
        agencies = []

        # Create List The Correct Size
        for _ in range(len(selectedAgencies)):
            values.append([])

        # Construct a 2d Array Of All Selected Crimes, stored by [Agency, Crime Type] (Yes this is the opposite of the one above, it had to be for the plot)
        for item in res:
            if (item[-1] in agencies):
                for i in range(len(item)):
                    if (i != 0 and i != (len(item) - 1)):
                        values[agencies.index(item[-1])][i - 1] += item[i]
            else:
                agencies.append(item[-1])
                #tempList = []
                for i in range(len(item)):
                    if (i != 0 and i != (len(item) - 1)):
                        values[agencies.index(item[-1])].append(item[i])

        # Unlike the other plots this one graphs a different plot for each Agency
        if (len(values) > 1):
            # This method returns an array if the supplied parameter is > 1, but a single object if the parameter is 1 which caused huge annoyances in debugging this
            # It is also why the above condition is neccessary
            # Enable Multiple Plots, otherwise they all overlap (example in 'Line')
            fig, axes = plt.subplots(len(values))

            # Repreatedly Draw Pie Charts with the appropiate Labels
            for i in range(len(values)):
                axes[i].pie(values[i], labels=columns[1:-1])
                axes[i].set_title("Crime Distribution in " + agencies[i])


        else:
            plt.pie(values[0], labels=columns[1:-1])
            plt.title("Crime Distribution in " + agencies[0])

        # Note we don't draw the legend in this version since it covers up the plot 

    plt.tight_layout()

    # Convert the Plot to an image and save the data to a buffer
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=200)
    buffer.seek(0)

    # Encode the buffer to allow it to be sent over to the template
    b64 = base64.b64encode(buffer.getvalue()).decode()

    buffer.close()

    context = {
        "query" : res,
        "columns" : columnnames,
        "selectedAgencies" : selectedAgencies,
        "selectedStates" : selectedStates,
        "selectedCrimeFamily" : selectedCrimeFamily,
        "selectAgencyType" : selectAgencyType,
        "selectedYears" : selectedYears,
        "finalQuery" : finalQuery,
        "graph" : b64 # Read by the template file
    }

    #respond 
    return HttpResponse(template.render(context, request))



    





