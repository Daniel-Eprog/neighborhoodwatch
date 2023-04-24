from django.http import HttpResponse
from django.template import loader
import getpass
import oracledb


pw = getpass.getpass("Enter password: ")

connection = oracledb.connect(
    user="esteban.medero",
    password=pw,
    dsn="oracle.cise.ufl.edu:1521/orcl")

print("Successfully connected to Oracle Database")

def index(request):
    
    cursor = connection.cursor()

    cursor.execute("SELECT SUM(num_rows) AS total_rows FROM all_tables")
    res = cursor.fetchall()
    print(res)

    #Load the necessary HTML templated to render data on
    template = loader.get_template("index.html")

    context = {
        "query" : res
    }

    #respond
    return HttpResponse(template.render(context, request))