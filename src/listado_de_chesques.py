from menu import Menu, Entry
from app import App
from pandas import DataFrame, read_csv
from datetime import datetime


ERROR: int = -1
OK: int = 0
SUCCESS: int = 1


OUTPUTS = ["PANTALLA", "CSV"]
STATUS = ["PENDIENTE", "APROBADO", "RECHAZADO", ""]
TYPES = ["EMITIDO", "DEPOSITADO"]


# El orden de los argumentos son los siguientes:
#    a. Nombre del archivo csv.
#    b. DNI del cliente donde se filtraran.
#    c. Salida: PANTALLA o CSV
#    d. Tipo de cheque: EMITIDO o DEPOSITADO
#    e. Estado del cheque: PENDIENTE, APROBADO, RECHAZADO. (Opcional)
#    f. Rango fecha: xx-xx-xxxx:yy-yy-yyyy (Opcional)
def obtain_parameters():

    def isNaN(num):
        return num != num

    file_path = input("\nEnter path for your .csv file: ")

    valid = False
    dni = 0

    while not valid:
        try:
            dni = int(input("Enter DNI number of a person to consult: "))
            valid = True
        except ValueError:
            print("[ERROR] Enter a valid DNI number (only numbers).")

    output = input("Enter wether the output should be console (PANTALLA) or a file (CSV): ")
    while output not in (OUTPUTS):
        output = input("Please, type either PANTALLA or CSV: ")

    type = input(
        "Select check type either EMITIDO or DEPOSITADO: ")
    while type.upper() not in (TYPES):
       type = input(
        "Please, type either EMITIDO or DEPOSITADO: ")     

    status = input(
        "Select status PENDIENTE, APROBADO, RECHAZADO (Optional): ")
    while status.upper() not in (STATUS):
        status = input(
            "Select either PENDIENTE, APROBADO, RECHAZADO (Optional): ")

    date_range = input(
        "Enter date range with format xx-xx-xxxx:yy-yy-yyyy (Optional): ")

    return file_path, dni, output, type, status, date_range


# Si el parámetro “Salida” es PANTALLA se deberá imprimir por pantalla todos
# los valores que se tienen, y si “Salida” es CSV se deberá exportar a un csv
# con las siguientes condiciones:
# a. El nombre de archivo tiene que tener el formato <DNI><TIMESTAMPS ACTUAL>.csv
# b. Se tiene que exportar las dos fechas, el valor del cheque y la cuenta
def export_checks(dni: int, checks: DataFrame, output_format: str):
    match output_format.upper():
        case "PANTALLA":
            print(checks)

        case "CSV":
            timestamp = datetime.timestamp(datetime.now())
            checks.to_csv(str(dni) + "_" + str(timestamp) +
                           ".csv", index=False)

        case _:
            raise("Can't export checks according to: " + output_format)


# Si para un DNI, dado un número de cheque de una misma cuenta de origen, se repite,
# se debe mostrar el error por pantalla, indicando que ese es el problema.
def verify_checks(checks: DataFrame):
    cheques_por_cuenta = checks.groupby("NumeroCuentaOrigen")

    for cuenta in cheques_por_cuenta.groups.keys():
        cheques = cheques_por_cuenta.get_group(cuenta)
        col_NroCheque = cheques["NroCheque"]
        if any(len(cheques[col_NroCheque == n]) > 1 for n in col_NroCheque.unique()):
            return ERROR

    return OK


# Si el estado del cheque no se pasa, se deberán imprimir
# los cheques sin filtrar por estado
def filter_by_status(checks: DataFrame, status: str):
    if status == "":
        return checks
    else:
        return checks[checks["Estado"] == status.upper()]


def checks_get_by_dni(dni: int, file_path: str):
    cheques: DataFrame
    try:
        cheques = read_csv(file_path)
    except Exception as error:
        print("Se produjo un error al intentar leer " + file_path)
        print(error)

    return cheques[cheques["DNI"] == dni]


def get_checks():
    urlfile, dni, output_format, _, status, _ = obtain_parameters()

    user_checks = checks_get_by_dni(dni, urlfile)

    if verify_checks(user_checks) == OK:
        filter_checks = filter_by_status(user_checks, status)
        export_checks(dni, filter_checks, output_format)
        return SUCCESS

    else:
        print("\n[ERROR] Repeated Check Number were found from same account for that DNI.")
        return ERROR


###############################################################################

app: App = App()

options: list[Entry] = [
    Entry("Consult checks", lambda: get_checks()),
    Entry("Exit", lambda: app.stop())
]

if __name__ == "__main__":
    app.start()

    menu: Menu = Menu()

    menu.load(options=options)

    print("Welcome to Py-Check your Check control system.", end="\n")

    while app.status == app.RUNNING:

        print("\nSelect an available option:", end="\n")

        menu.show()

        print(">>> ", end="")

        if menu.select() != ERROR:
            if menu.execute() != ERROR:
                continue

        app.stop()
