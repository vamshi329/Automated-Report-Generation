import pandas as pd
from fpdf import FPDF
import os # To handle file paths

class PDFReport(FPDF):
    """
    Custom FPDF class to add header and footer consistently.
    """
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Monthly Sales Performance Report', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

def read_and_analyze_data(file_path):
    """
    Reads sales data from a CSV, calculates total sales and product-wise revenue.

    Args:
        file_path (str): The path to the CSV data file.

    Returns:
        tuple: A tuple containing:
            - pandas.DataFrame: Aggregated sales data per product.
            - float: Total revenue from all sales.
            - str: Name of the top selling product.
    """
    try:
        df = pd.read_csv(file_path)

        # Ensure numeric types for calculations
        df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')
        df['UnitPrice'] = pd.to_numeric(df['UnitPrice'], errors='coerce')

        # Drop rows where conversion failed
        df.dropna(subset=['Quantity', 'UnitPrice'], inplace=True)

        # Calculate TotalPrice for each transaction
        df['TotalPrice'] = df['Quantity'] * df['UnitPrice']

        # Group by product to get total quantity and revenue
        product_summary = df.groupby('Product').agg(
            TotalQuantity=('Quantity', 'sum'),
            TotalRevenue=('TotalPrice', 'sum')
        ).reset_index()

        # Calculate overall total revenue
        total_revenue = df['TotalPrice'].sum()

        # Find the top selling product by revenue
        top_selling_product = ""
        if not product_summary.empty:
            top_selling_product = product_summary.loc[product_summary['TotalRevenue'].idxmax()]['Product']

        return product_summary, total_revenue, top_selling_product

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return pd.DataFrame(), 0, ""
    except Exception as e:
        print(f"An error occurred during data reading or analysis: {e}")
        return pd.DataFrame(), 0, ""

def generate_sales_report(product_summary_df, total_revenue, top_selling_product, output_filename="Sales_Performance_Report.pdf"):
    """
    Generates a PDF sales report based on the analyzed data.

    Args:
        product_summary_df (pandas.DataFrame): DataFrame with product-wise summary.
        total_revenue (float): The overall total revenue.
        top_selling_product (str): The name of the top-selling product.
        output_filename (str): The name of the output PDF file.
    """
    pdf = PDFReport()
    pdf.alias_nb_pages() # For total page count in footer
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15) # Enable auto page break

    # Section 1: Executive Summary
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Executive Summary', 0, 1, 'L')
    pdf.ln(5)

    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 8, f"This report provides an overview of sales performance. "
                            f"The total revenue generated is ${total_revenue:,.2f}. "
                            f"The top-selling product by revenue is '{top_selling_product}'.")
    pdf.ln(10)

    # Section 2: Product-wise Sales Performance
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Product-wise Sales Performance', 0, 1, 'L')
    pdf.ln(5)

    if not product_summary_df.empty:
        # Table Headers
        pdf.set_font('Arial', 'B', 10)
        col_width = pdf.w / 4.5 # Roughly distribute width
        pdf.cell(col_width, 10, 'Product', 1, 0, 'C')
        pdf.cell(col_width, 10, 'Total Quantity', 1, 0, 'C')
        pdf.cell(col_width, 10, 'Total Revenue ($)', 1, 1, 'C') # 1 for border, 1 for new line

        # Table Data
        pdf.set_font('Arial', '', 10)
        for index, row in product_summary_df.iterrows():
            pdf.cell(col_width, 10, str(row['Product']), 1, 0, 'L')
            pdf.cell(col_width, 10, str(int(row['TotalQuantity'])), 1, 0, 'R')
            pdf.cell(col_width, 10, f"${row['TotalRevenue']:,.2f}", 1, 1, 'R')
    else:
        pdf.set_font('Arial', 'I', 12)
        pdf.cell(0, 10, "No product sales data to display.", 0, 1, 'L')

    # Save the PDF
    try:
        pdf.output(output_filename)
        print(f"\nReport successfully generated: {os.path.abspath(output_filename)}")
    except Exception as e:
        print(f"Error saving PDF report: {e}")

if __name__ == "__main__":
    csv_file = 'sales_data.csv'
    output_pdf_file = 'Sales_Performance_Report.pdf'

    # --- Task Execution ---
    print(f"Reading and analyzing data from '{csv_file}'...")
    product_summary, total_revenue, top_selling_product = read_and_analyze_data(csv_file)

    if not product_summary.empty:
        print("\nData Analysis Summary:")
        print(f"Total Revenue: ${total_revenue:,.2f}")
        print(f"Top Selling Product: {top_selling_product}")
        print("\nProduct-wise Summary:")
        print(product_summary.to_string(index=False, float_format="%.2f"))

        print(f"\nGenerating PDF report '{output_pdf_file}'...")
        generate_sales_report(product_summary, total_revenue, top_selling_product, output_pdf_file)
    else:
        print("Could not generate report due to missing or empty data.")