from robocorp.tasks import task
from robocorp import browser

from RPA.Archive import Archive
from RPA.HTTP import HTTP
from RPA.PDF import PDF
from RPA.Tables import Tables

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        browser_engine="firefox",
    )
    open_robot_order_website()
    download_csv_file()
    orders = get_orders()

    for order in orders:
        # log_order(order)
        fill_the_form(order)
        

    archive_receipts()

def open_robot_order_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def download_csv_file():
    """Downloads csv file from the given URL"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

def get_orders():
    """Convert csv to Table"""
    library = Tables()
    orders = library.read_table_from_csv(
    "orders.csv", columns=["Order number", "Head", "Body", "Legs", "Address"]
    )
    return orders
    
def log_order(order):
    """Log each order row"""
    print(order)

def close_annoying_modal():
    """Close annoying Modal"""
    page = browser.page()
    page.click("button:text('Ok')")

def fill_the_form(order):
    """Fill the form of the order of the robot"""
    close_annoying_modal()

    page = browser.page()
    page.select_option("#head", index=int(order["Head"]))
    page.click(f'input[value="{int(order["Body"])}"]')
    page.fill('input[placeholder="Enter the part number for the legs"]', str(order["Legs"]))
    page.fill('#address', str(order["Address"]))
    page.click("text=Preview")

    while True:
        page.click("button:text('Order')")

        error_element = page.query_selector(".alert.alert-danger")

        if error_element:
            # print("Error message detected. Retrying order submission...")
            # Retry clicking the order button
            continue
        else:
            # If no error, proceed with clicking "Order"
            break

    pdf_file = store_receipt_as_pdf(order["Order number"])
    screenshot = screenshot_robot(order["Order number"])
    embed_screenshot_to_receipt(screenshot, pdf_file)

def store_receipt_as_pdf(order_number):
    """Export the data to a pdf file"""
    page = browser.page()
    sales_results_html = page.locator("#order-completion").inner_html()

    pdf = PDF()
    pdf.html_to_pdf(sales_results_html, f'output/receipts/{order_number}.pdf')
    return f'output/receipts/{order_number}.pdf'

def screenshot_robot(order_number):
    """Take a screenshot of the robot preview"""
    page = browser.page()

    selector = f'#robot-preview-image'
    page.screenshot(path=f'output/receipts/{order_number}.png',clip=page.query_selector(selector).bounding_box())
    return f'output/receipts/{order_number}.png'

def embed_screenshot_to_receipt(screenshot, pdf_file):
    page = browser.page()
    pdf = PDF()

    pdf.add_watermark_image_to_pdf(
        image_path=f"{screenshot}",
        source_path=f"{pdf_file}",
        output_path=f"{pdf_file}"
    )

    page.click("button:text('Order another robot')")

def archive_receipts():
    lib = Archive()

    lib.archive_folder_with_zip('./output/receipts', './output/receipts.zip', include='*.pdf', exclude='*.png')



    
