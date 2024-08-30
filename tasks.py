from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.FileSystem import FileSystem
from RPA.Tables import Tables
from RPA.PDF import PDF

from fpdf import FPDF
import shutil

@task
def open_robot_order_website():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=500,
    )

    orders = get_orders()
    make_orders(orders)
    make_zip()
    

def get_orders():
    """
    Consults the orders from a file in csv format.
    Downloads the file, places it in "output".
    Creates a table variable and returns it.
    """
    output_path = "output/orders.csv"
    http = HTTP()
    http.download(
        url="https://robotsparebinindustries.com/orders.csv", target_file=output_path, overwrite=True)
    
    tables = Tables()
    table = orders_table = tables.read_table_from_csv(output_path)
    return table

def make_orders(orders):
    """
    Starts the order making process by going to the store page in browser.
    Creates a dictionary that refers to the specific option required.
    Generates a for loop that keeps filling the form based on the "orders" argument.
    """

    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    
    robot_heads = {
    "1": "Roll-a-thor",
    "2": "Peanut crusher",
    "3": "D.A.V.E",
    "4": "Andy Roid",
    "5": "Spanner mate",
    "6": "Drillbit 2000"
    }

    for order in orders:
        close_annoying_modal()
        fill_form(order, robot_heads)

def close_annoying_modal():
    """
    Closes the modal that requires to sell constitutional rights.
    """

    page = browser.page()
    close_button = "button.btn.btn-dark"
    page.click(close_button)

def fill_form(order, robot_heads):
    """
    Executes the action of filling the form.
    validates with retries if an error appears when pressing "order".
    Calls another function to create the order PDF.
    Calls another function to click a button to return to the beginning.
    """

    page = browser.page()

    order_number = order["Order number"]
    head = robot_heads[order["Head"]] + " head"
    body = "#id-body-" + order["Body"]
    
    page.select_option("select#head.custom-select", head)
    page.click(body)
    page.fill(".form-control", str(order["Legs"]))
    page.fill("#address", order["Address"])
    
    max_retries = 10
    retries = 0

    while retries < max_retries:
        page.click("#order")
    
        page.wait_for_timeout(2000) 

        if page.is_visible("div.alert.alert-danger"):
            retries += 1
            print(f"Submit failed, retrying... ({retries}/{max_retries})")
        else:
            print("Order submitted successfully.")
            break
    
    store_receipt_as_pdf(order_number)
    new_order()

def new_order():
    """
    Clicks the button to order again after making an order.
    """

    page = browser.page()
    page.click("#order-another")

def store_receipt_as_pdf(order_number):
    """
    Creates the pdf with the image of the order.
    """
    page = browser.page()
    pdf = PDF()

    output_path = "output/orders/" + "screenshot_" + str(order_number) + ".png"
    page.screenshot(path=output_path)

    file = FPDF()
    file.add_page()
    file.image(output_path, x=10, y=10, w=180)
    output_path = "output/orders/" + "order_" + str(order_number) + ".pdf"
    file.output(output_path)
    
def make_zip():
    """
    Makes a ZIP file for the files inside of "orders"
    """

    pdf_folder = "output/orders/"
    zip_filename = "output/orders_receipts.zip"

    shutil.make_archive(zip_filename.replace('.zip', ''), 'zip', pdf_folder)
    
