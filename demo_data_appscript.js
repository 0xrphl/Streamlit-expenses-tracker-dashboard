/**
 * ============================================================
 * Google Apps Script — Populate Demo Data
 * ============================================================
 * 
 * HOW TO USE:
 * 1. Open your Google Sheet
 * 2. Go to Extensions → Apps Script
 * 3. Delete any existing code and paste this entire file
 * 4. Click the ▶ Run button (select "populateDemoData")
 * 5. Authorize the script when prompted
 * 6. Check your sheet — both tabs are now populated!
 * 
 * This script will:
 * - Clear existing data in "Table 1" and "Table 2 Fixed expenses"
 * - Create the tabs if they don't exist
 * - Populate with generic demo data (no personal information)
 * ============================================================
 */

function populateDemoData() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // Create or get Table 1
  var table1 = getOrCreateSheet(ss, "Table 1");
  // Create or get Table 2
  var table2 = getOrCreateSheet(ss, "Table 2 Fixed expenses");
  
  // Clear existing data
  table1.clear();
  table2.clear();
  
  // Populate Table 1
  populateTable1(table1);
  
  // Populate Table 2
  populateTable2(table2);
  
  SpreadsheetApp.getUi().alert(
    "✅ Demo data populated!\n\n" +
    "Table 1: " + (table1.getLastRow() - 1) + " transactions\n" +
    "Table 2: " + (table2.getLastRow() - 1) + " fixed expenses"
  );
}

function getOrCreateSheet(ss, name) {
  var sheet = ss.getSheetByName(name);
  if (!sheet) {
    sheet = ss.insertSheet(name);
  }
  return sheet;
}

function populateTable1(sheet) {
  // Headers
  var headers = [
    "event", "date", "month", "type_of_expense", 
    "transaction_category", "amountCOP", "distribution", 
    "details", "origin"
  ];
  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  sheet.getRange(1, 1, 1, headers.length).setFontWeight("bold");
  
  // Demo transaction data — generic, no personal info
  var data = [
    // ---- January 2026 ----
    ["Expense", "01/01/2026", "2026-01-January", "Fixed", "Housing and basic services", "1,800,000", "50/50", "Mortgage Partner 2", "Savings account Partner 2"],
    ["Expense", "01/02/2026", "2026-01-January", "Fixed", "Housing and basic services", "1,100,000", "50/50", "Mortgage Partner 1", "Savings account Partner 1"],
    ["Expense", "01/03/2026", "2026-01-January", "Fixed", "Food and other groceries", "91,000", "50/50", "D1", "Savings account Partner 2"],
    ["Expense", "01/03/2026", "2026-01-January", "One time", "Entertainment and luxury", "60,000", "50/50", "Weekend outing", "Savings account Partner 2"],
    ["Expense", "01/04/2026", "2026-01-January", "One time", "Food and other groceries", "46,000", "50/50", "Delivery and restaurants", "Savings account Partner 2"],
    ["Expense", "01/05/2026", "2026-01-January", "Fixed", "Transportation", "16,000", "50/50", "Uber", "Savings account Partner 2"],
    ["Expense", "01/05/2026", "2026-01-January", "One time", "Food and other groceries", "70,000", "50/50", "Delivery and restaurants", "Savings account Partner 2"],
    ["Expense", "01/06/2026", "2026-01-January", "Fixed", "Transportation", "10,000", "50/50", "Uber", "Savings account Partner 2"],
    ["Expense", "01/07/2026", "2026-01-January", "One time", "Food and other groceries", "52,000", "50/50", "Delivery and restaurants", "Savings account Partner 2"],
    ["Expense", "01/08/2026", "2026-01-January", "Fixed", "Food and other groceries", "71,000", "50/50", "D1", "Savings account Partner 2"],
    ["Expense", "01/09/2026", "2026-01-January", "Fixed", "Housing and basic services", "60,000", "50/50", "Gas bill", "Savings account Partner 2"],
    ["Expense", "01/10/2026", "2026-01-January", "Fixed", "Health and taxes", "920,000", "50/50", "Social security", "Savings account Partner 2"],
    ["Expense", "01/10/2026", "2026-01-January", "Fixed", "Transportation", "9,700", "50/50", "Uber", "Savings account Partner 2"],
    ["Expense", "01/10/2026", "2026-01-January", "Fixed", "Food and other groceries", "730,900", "50/50", "Wholesale groceries", "Savings account Partner 2"],
    ["Expense", "01/10/2026", "2026-01-January", "Fixed", "Clothing and other basic expenses", "35,000", "Partner 1", "Grooming", "Savings account Partner 2"],
    ["Expense", "01/11/2026", "2026-01-January", "Fixed", "Pets", "150,000", "50/50", "Dogs food", "Savings account Partner 2"],
    ["Expense", "01/11/2026", "2026-01-January", "Fixed", "Food and other groceries", "327,300", "50/50", "Groceries wholesale", "Savings account Partner 2"],
    ["Expense", "01/12/2026", "2026-01-January", "Fixed", "Pets", "38,000", "50/50", "Pets insurance", "Savings account Partner 2"],
    ["Expense", "01/12/2026", "2026-01-January", "One time", "Entertainment and luxury", "254,000", "50/50", "Online shopping", "Savings account Partner 2"],
    ["Expense", "01/15/2026", "2026-01-January", "One time", "Entertainment and luxury", "70,000", "Partner 1", "Headphones", "Savings account Partner 2"],
    ["Expense", "01/17/2026", "2026-01-January", "Fixed", "Entertainment and luxury", "90,000", "Partner 2", "Nails", "Savings account Partner 2"],
    ["Expense", "01/17/2026", "2026-01-January", "Fixed", "Housing and basic services", "500,000", "50/50", "Maid", "Rent"],
    ["Expense", "01/17/2026", "2026-01-January", "Fixed", "Food and other groceries", "75,500", "50/50", "Delivery and restaurants", "Savings account Partner 2"],
    ["Expense", "01/18/2026", "2026-01-January", "Fixed", "Clothing and other basic expenses", "35,000", "Partner 1", "Grooming", "Savings account Partner 2"],
    ["Expense", "01/19/2026", "2026-01-January", "Fixed", "Housing and basic services", "110,000", "Partner 2", "Dentist", "Savings account Partner 2"],
    ["Expense", "01/20/2026", "2026-01-January", "Fixed", "Food and other groceries", "30,000", "50/50", "D1", "Savings account Partner 2"],
    ["Income", "01/20/2026", "2026-01-January", "Fixed", "Payroll", "12,000,000", "Partner 2", "Payroll", "Savings account Partner 2"],
    ["Income", "01/25/2026", "2026-01-January", "Fixed", "Payroll", "10,000,000", "Partner 1", "Payroll", "Savings account Partner 1"],
    ["Expense", "01/24/2026", "2026-01-January", "Fixed", "Housing and basic services", "292,300", "50/50", "Water bill", "Savings account Partner 2"],
    ["Expense", "01/25/2026", "2026-01-January", "Fixed", "Pets", "65,000", "50/50", "Cat food", "Savings account Partner 2"],
    ["Expense", "01/25/2026", "2026-01-January", "Fixed", "Food and other groceries", "426,000", "50/50", "Groceries wholesale", "Savings account Partner 2"],
    ["Expense", "01/25/2026", "2026-01-January", "Fixed", "Codependents", "1,100,000", "Partner 1", "Family allowance", "Savings account Partner 1"],
    ["Expense", "01/27/2026", "2026-01-January", "Fixed", "Food and other groceries", "15,600", "50/50", "D1", "Savings account Partner 2"],
    ["Expense", "01/30/2026", "2026-01-January", "Fixed", "Housing and basic services", "500,000", "50/50", "Maid", "Savings account Partner 2"],
    ["Expense", "01/31/2026", "2026-01-January", "Fixed", "Housing and basic services", "121,900", "50/50", "Internet bill", "Savings account Partner 2"],

    // ---- February 2026 ----
    ["Expense", "02/01/2026", "2026-02-February", "Fixed", "Food and other groceries", "150,000", "50/50", "Delivery and restaurants", "Savings account Partner 2"],
    ["Expense", "02/01/2026", "2026-02-February", "Fixed", "Transportation", "10,000", "50/50", "Uber", "Savings account Partner 2"],
    ["Expense", "02/02/2026", "2026-02-February", "Fixed", "Housing and basic services", "1,714,000", "50/50", "Mortgage Partner 2", "Savings account Partner 2"],
    ["Expense", "02/05/2026", "2026-02-February", "Fixed", "Health and taxes", "820,000", "50/50", "Social security", "Savings account Partner 2"],
    ["Expense", "02/07/2026", "2026-02-February", "Fixed", "Codependents", "2,000,000", "Partner 2", "Family allowance", "Savings account Partner 2"],
    ["Expense", "02/08/2026", "2026-02-February", "Fixed", "Food and other groceries", "43,000", "50/50", "Delivery and restaurants", "Savings account Partner 2"],
    ["Expense", "02/08/2026", "2026-02-February", "Fixed", "Transportation", "12,000", "50/50", "Uber", "Savings account Partner 2"],
    ["Expense", "02/09/2026", "2026-02-February", "Fixed", "Housing and basic services", "110,000", "Partner 2", "Dentist", "Savings account Partner 2"],
    ["Expense", "02/10/2026", "2026-02-February", "Fixed", "Food and other groceries", "75,000", "50/50", "D1", "Savings account Partner 2"],
    ["Expense", "02/11/2026", "2026-02-February", "Fixed", "Pets", "38,000", "50/50", "Pets insurance", "Savings account Partner 2"],
    ["Expense", "02/13/2026", "2026-02-February", "Fixed", "Housing and basic services", "600,000", "50/50", "Maid", "Savings account Partner 2"],
    ["Expense", "02/13/2026", "2026-02-February", "Fixed", "Bank fees", "11,200", "Partner 2", "Account fee", "Savings account Partner 2"],
    ["Expense", "02/15/2026", "2026-02-February", "One time", "Housing and basic services", "165,600", "50/50", "Hardware store", "Savings account Partner 2"],
    ["Expense", "02/15/2026", "2026-02-February", "Fixed", "Entertainment and luxury", "38,000", "50/50", "Grooming", "Savings account Partner 2"],
    ["Expense", "02/16/2026", "2026-02-February", "Fixed", "Entertainment and luxury", "85,000", "Partner 2", "Nails", "Savings account Partner 2"],
    ["Expense", "02/19/2026", "2026-02-February", "Fixed", "Housing and basic services", "850,000", "50/50", "Mortgage Partner 1", "Savings account Partner 1"],
    ["Expense", "02/19/2026", "2026-02-February", "Fixed", "Housing and basic services", "300,000", "50/50", "Mortgage Partner 1", "Savings account Partner 2"],
    ["Income", "02/19/2026", "2026-02-February", "Fixed", "Payroll", "12,000,000", "Partner 2", "Payroll", "Savings account Partner 2"],
    ["Income", "02/19/2026", "2026-02-February", "Fixed", "Payroll", "10,000,000", "Partner 1", "Payroll", "Savings account Partner 1"],
    ["Expense", "02/20/2026", "2026-02-February", "Fixed", "Housing and basic services", "145,620", "50/50", "Water bill", "Savings account Partner 2"],
    ["Expense", "02/22/2026", "2026-02-February", "One time", "Pets", "445,000", "50/50", "Vet vaccines", "Savings account Partner 2"],
    ["Expense", "02/23/2026", "2026-02-February", "Fixed", "Food and other groceries", "100,000", "50/50", "Delivery and restaurants", "Savings account Partner 2"],
    ["Expense", "02/25/2026", "2026-02-February", "Fixed", "Housing and basic services", "187,000", "50/50", "Electric bill", "Savings account Partner 1"],
    ["Expense", "02/25/2026", "2026-02-February", "Fixed", "Housing and basic services", "1,162,000", "50/50", "HOA admin fee", "Savings account Partner 1"],
    ["Expense", "02/25/2026", "2026-02-February", "Fixed", "Codependents", "400,000", "Partner 1", "Family allowance", "Savings account Partner 1"],
    ["Expense", "02/25/2026", "2026-02-February", "Fixed", "Housing and basic services", "163,400", "50/50", "Internet bill", "Savings account Partner 2"],
    ["Expense", "02/26/2026", "2026-02-February", "Fixed", "Food and other groceries", "1,796,168", "50/50", "Groceries wholesale", "Savings account Partner 2"],
    ["Expense", "02/27/2026", "2026-02-February", "Fixed", "Housing and basic services", "600,000", "50/50", "Maid", "Savings account Partner 2"],
    ["Expense", "02/28/2026", "2026-02-February", "Fixed", "Entertainment and luxury", "38,000", "Partner 1", "Grooming", "Savings account Partner 2"],

    // ---- March 2026 ----
    ["Expense", "03/01/2026", "2026-03-March", "Fixed", "Food and other groceries", "70,500", "50/50", "Delivery and restaurants", "Savings account Partner 2"],
    ["Expense", "03/01/2026", "2026-03-March", "Fixed", "Food and other groceries", "32,500", "50/50", "Dollar store", "Savings account Partner 2"],
    ["Expense", "03/01/2026", "2026-03-March", "Fixed", "Transportation", "12,000", "50/50", "Uber", "Savings account Partner 2"],
    ["Expense", "03/04/2026", "2026-03-March", "Fixed", "Food and other groceries", "93,600", "50/50", "D1", "Savings account Partner 2"],
    ["Expense", "03/05/2026", "2026-03-March", "Fixed", "Transportation", "17,000", "50/50", "Uber", "Savings account Partner 2"],
    ["Expense", "03/07/2026", "2026-03-March", "Fixed", "Entertainment and luxury", "38,000", "Partner 1", "Grooming", "Savings account Partner 2"],
    ["Income", "03/07/2026", "2026-03-March", "One time", "Housing and basic services", "1,140,000", "50/50", "Rent", "Savings account Partner 2"],
    ["Expense", "03/10/2026", "2026-03-March", "Fixed", "Food and other groceries", "114,000", "50/50", "D1", "Savings account Partner 2"],
    ["Expense", "03/11/2026", "2026-03-March", "Fixed", "Housing and basic services", "127,900", "50/50", "Gas bill", "Rent"],
    ["Expense", "03/11/2026", "2026-03-March", "Fixed", "Health and taxes", "820,000", "50/50", "Social security", "Savings account Partner 2"],
    ["Expense", "03/11/2026", "2026-03-March", "Fixed", "Pets", "60,000", "50/50", "Cat litter", "Savings account Partner 2"],
    ["Expense", "03/13/2026", "2026-03-March", "Fixed", "Pets", "38,000", "50/50", "Pets insurance", "Savings account Partner 2"],
    ["Expense", "03/13/2026", "2026-03-March", "Fixed", "Housing and basic services", "600,000", "50/50", "Maid", "Savings account Partner 2"],
    ["Expense", "03/13/2026", "2026-03-March", "One time", "Entertainment and luxury", "105,000", "50/50", "Recreation", "Savings account Partner 2"],
    ["Expense", "03/20/2026", "2026-03-March", "Fixed", "Housing and basic services", "470,000", "50/50", "Mortgage Partner 1", "Savings account Partner 1"],
    ["Expense", "03/20/2026", "2026-03-March", "Fixed", "Housing and basic services", "644,000", "50/50", "Mortgage Partner 1", "Savings account Partner 2"],
    ["Expense", "03/20/2026", "2026-03-March", "Fixed", "Food and other groceries", "591,000", "50/50", "Groceries wholesale", "Savings account Partner 2"],
    ["Expense", "03/24/2026", "2026-03-March", "Fixed", "Memberships and subscriptions", "44,900", "50/50", "Netflix", "Savings account Partner 2"],
    ["Expense", "03/25/2026", "2026-03-March", "Fixed", "Food and other groceries", "136,250", "50/50", "D1", "Savings account Partner 2"],
    ["Expense", "03/28/2026", "2026-03-March", "Fixed", "Housing and basic services", "121,900", "50/50", "Internet bill", "Savings account Partner 2"],
    ["Expense", "03/30/2026", "2026-03-March", "Fixed", "Entertainment and luxury", "38,000", "Partner 1", "Grooming", "Savings account Partner 2"],
    ["Expense", "03/30/2026", "2026-03-March", "One time", "Entertainment and luxury", "284,000", "Partner 2", "Online shopping", "Savings account Partner 2"],
  ];
  
  if (data.length > 0) {
    sheet.getRange(2, 1, data.length, data[0].length).setValues(data);
  }
}

function populateTable2(sheet) {
  // Headers
  var headers = [
    "event", "date", "month", "type_of_expense", "transaction_category",
    "amountCOP", "details", "distribution", "origin", 
    "amount_paid%", "one_payment", "months_valid"
  ];
  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  sheet.getRange(1, 1, 1, headers.length).setFontWeight("bold");
  
  // Fixed expenses budget — January
  var dataJan = [
    ["Expense", "1/1/2026", "2026-01-January", "Fixed", "Housing and basic services", "1,800,000", "Mortgage Partner 2", "50/50", "Savings account Partner 2", 100, true, 1],
    ["Expense", "1/1/2026", "2026-01-January", "Fixed", "Housing and basic services", "1,100,000", "Mortgage Partner 1", "50/50", "Savings account Partner 1", 100, true, 1],
    ["Expense", "1/1/2026", "2026-01-January", "Fixed", "Housing and basic services", "150,000", "Electric bill", "50/50", "Savings account Partner 1", 0, true, 1],
    ["Expense", "1/1/2026", "2026-01-January", "Fixed", "Housing and basic services", "110,000", "Water bill", "50/50", "Savings account Partner 2", 265.7, true, 1],
    ["Expense", "1/1/2026", "2026-01-January", "Fixed", "Housing and basic services", "130,000", "Internet bill", "50/50", "Savings account Partner 2", 93.8, true, 1],
    ["Expense", "1/1/2026", "2026-01-January", "Fixed", "Health and taxes", "820,000", "Social security", "50/50", "Savings account Partner 1", 112.2, true, 1],
    ["Expense", "1/1/2026", "2026-01-January", "Fixed", "Memberships and subscriptions", "50,000", "Netflix", "50/50", "Savings account Partner 1", 0, true, 1],
    ["Expense", "1/1/2026", "2026-01-January", "Fixed", "Pets", "90,000", "Cat litter", "50/50", "Savings account Partner 2", 100, true, 2],
    ["Expense", "1/1/2026", "2026-01-January", "Fixed", "Pets", "65,000", "Cat food", "50/50", "Savings account Partner 2", 100, true, 2],
    ["Expense", "1/1/2026", "2026-01-January", "Fixed", "Pets", "150,000", "Dogs food", "50/50", "Savings account Partner 2", 100, true, 1],
    ["Expense", "1/1/2026", "2026-01-January", "Fixed", "Housing and basic services", "380,000", "HOA admin fee", "50/50", "Savings account Partner 1", 0, true, 1],
    ["Expense", "1/1/2026", "2026-01-January", "Fixed", "Codependents", "800,000", "Family allowance", "Partner 1", "Savings account Partner 1", 137.5, true, 1],
    ["Expense", "1/1/2026", "2026-01-January", "Fixed", "Codependents", "800,000", "Family allowance P2", "Partner 2", "Savings account Partner 2", 0, true, 1],
    ["Expense", "1/1/2026", "2026-01-January", "Fixed", "Bank fees", "16,000", "Credit card fee", "Partner 2", "Savings account Partner 2", 0, true, 1],
    ["Expense", "1/1/2026", "2026-01-January", "Fixed", "Bank fees", "30,000", "Account fee", "Partner 2", "Savings account Partner 2", 0, true, 1],
    ["Expense", "1/1/2026", "2026-01-January", "Fixed", "Housing and basic services", "70,000", "Gas bill", "50/50", "Savings account Partner 2", 85.7, true, 1],
    ["Expense", "1/1/2026", "2026-01-January", "Fixed", "Housing and basic services", "1,200,000", "Maid", "50/50", "Savings account Partner 2", 83.3, true, 1],
    ["Expense", "1/1/2026", "2026-01-January", "Fixed", "Food and other groceries", "500,000", "Delivery and restaurants", "50/50", "Savings account Partner 2", 164.9, false, 1],
    ["Expense", "1/1/2026", "2026-01-January", "Fixed", "Food and other groceries", "900,000", "Wholesale groceries", "50/50", "Savings account Partner 2", 81.2, false, 1],
    ["Expense", "1/1/2026", "2026-01-January", "Fixed", "Food and other groceries", "700,000", "Groceries wholesale", "50/50", "Savings account Partner 2", 107.6, false, 1],
    ["Expense", "1/1/2026", "2026-01-January", "Fixed", "Food and other groceries", "500,000", "Groceries supermarket", "50/50", "Savings account Partner 2", 42.2, false, 1],
    ["Expense", "1/1/2026", "2026-01-January", "Fixed", "Food and other groceries", "300,000", "Dollar store", "50/50", "Savings account Partner 2", 30.3, false, 1],
    ["Expense", "1/1/2026", "2026-01-January", "Fixed", "Food and other groceries", "200,000", "D1", "50/50", "Savings account Partner 2", 224.1, false, 1],
    ["Expense", "1/1/2026", "2026-01-January", "Fixed", "Transportation", "300,000", "Uber", "50/50", "Savings account Partner 2", 61.5, false, 1],
    ["Expense", "1/1/2026", "2026-01-January", "Fixed", "Pets", "40,000", "Pets insurance", "50/50", "Savings account Partner 2", 95, true, 1],
    ["Expense", "1/1/2026", "2026-01-January", "Fixed", "Clothing and other basic expenses", "140,000", "Grooming", "Partner 1", "Savings account Partner 1", 110.7, false, 1],
    ["Expense", "1/1/2026", "2026-01-January", "Fixed", "Clothing and other basic expenses", "90,000", "Nails", "Partner 2", "Savings account Partner 2", 100, true, 1],
    ["Expense", "1/1/2026", "2026-01-January", "Fixed", "Housing and basic services", "110,000", "Dentist", "Partner 2", "Savings account Partner 2", 100, true, 1],
  ];
  
  if (dataJan.length > 0) {
    sheet.getRange(2, 1, dataJan.length, dataJan[0].length).setValues(dataJan);
  }
}

/**
 * Helper: Clear ALL data and start fresh
 * Run this if you want to wipe everything and re-populate
 */
function clearAllData() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  
  var table1 = ss.getSheetByName("Table 1");
  if (table1) table1.clear();
  
  var table2 = ss.getSheetByName("Table 2 Fixed expenses");
  if (table2) table2.clear();
  
  SpreadsheetApp.getUi().alert("All data cleared! Run populateDemoData() to repopulate.");
}
