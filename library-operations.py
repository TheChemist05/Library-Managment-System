import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def get_all_books_catalog(conn):
    """
    Query all rows in the books_catalog table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM books_catalog")

    rows = cur.fetchall()

    for row in rows:
        print(row)

def get_all_members(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM members")

    rows = cur.fetchall()

    for row in rows:
        print(row)

def get_all_books_inventory(conn):
    cur = conn.cursor()
    cur.execute("SELECT books_catalog.book_name, status, books_catalog.book_id  \
                 FROM books_inventory, books_catalog \
                 WHERE books_catalog.book_id = books_inventory.book_id \
                 ")

    rows = cur.fetchall()
    
    #print("\n ============--------------==============")
    #print(rows)
    #print("============--------------============== \n")
    
    
    bookInventory = {}
    bookName = ''
    bookStatus = 0
    bookID = 0
    
    for row in rows:
        bookName = row[0]
        bookStatus = row[1]
        bookID = row[2]
        #print("--", bookName, " -- ", bookStatus, "--ID--", bookID)
        
        if bookName not in bookInventory :
           #print("Adding book to dict: ", bookName)
           bookInventory[bookName] = [0, 0, 0, 0]
        
        bookstatusList =  bookInventory[bookName]
        #print (bookName, bookstatusList)
        count = 0
        bookstatusList[3] = bookID
        
        if bookStatus == 0:
           count = bookstatusList[0]
           count = count + 1
           bookstatusList[0] = count
        elif bookStatus == 1:
           count = bookstatusList[1]
           count = count + 1
           bookstatusList[1] = count
        elif bookStatus == 2:
           count = bookstatusList[2]
           count = count + 1
           bookstatusList[2] = count
        else:
           print('Invalid book status\n')
    #print("complete book list with status\n")
    print("-".rjust(10,'-'), "   ", "-".ljust(45, '-'), "-".rjust(10,'-'), "-".rjust(10, '-'), "-".rjust(10, '-'))
    print("Book ID".rjust(10,' '), "   ", "Book Name".ljust(45, ' '), "Availabile".rjust(10,' '), "Issued".rjust(10, ' '), "Missing".rjust(10, ' '))
    print("-".rjust(10,'-'), "   ", "-".ljust(45, '-'), "-".rjust(10,'-'), "-".rjust(10, '-'), "-".rjust(10, '-'))
    #print("Book ID\t\tBookName\t\tAvailable\t\tIssued\t\tMissing")
    #print("-------\t\t--------\t\t---------\t\t-------\t\t------")
    for book in bookInventory:
        print("{0:10d}".format(bookInventory[book][3]),"   ", book.ljust(45,' '), "{0:10d}".format(bookInventory[book][0]), "{0:10d}".format(bookInventory[book][1]),"{0:10d}".format(bookInventory[book][2]))
    #print(bookInventory)
    print("-".rjust(10,'-'), "   ", "-".ljust(45, '-'), "-".rjust(10,'-'), "-".rjust(10, '-'), "-".rjust(10, '-'))         
   
        

def return_book_by_book_id(bookID, memberID, conn):
    cur = conn.cursor()
    
    res = cur.execute("SELECT first_name FROM members where member_id = :memid",{"memid":memberID})
    row = res.fetchone()
    memberName = ''
    if row is None :
       return print("Member doesn't exist")
    else :
       print("\nReturning book by member = ", row[0])
       memberName = row[0]

    res = cur.execute("SELECT bc.book_checkout_id, bc.book_item_id  \
                       FROM books_inventory bi, book_checkout bc \
                       where bi.book_id = :bookid AND bi.status = 1 \
                       AND bc.book_item_id = bi.book_item_id \
                       AND bc.member_id = :memid", {"bookid":bookID, "memid":memberID} )
    row = res.fetchall()
    bookitemId = None
    bookchkId = None
    if row is None or len(row) == 0:
       return print("Error: the Book you are returning is not borrowed by --> ", memberName)
    else :
       print("Borrowed book details = ", row)
       bookitemId = row[0][1]
       bookchkId = row[0][0]
       print ("Returning book item: ", bookitemId)
     
    cur.execute("UPDATE books_inventory \
                 SET status = 0 \
                 WHERE book_item_id = :itemid", {"itemid":bookitemId}) 
    
    cur.execute("DELETE FROM book_checkout WHERE book_checkout_id  = :bchkid", {"bchkid":bookchkId})
    
    conn.commit()   

def borrow_book_by_book_id(bookID, memberID, conn):
    cur = conn.cursor()
    
    res = cur.execute("SELECT first_name FROM members where member_id = :memid",{"memid":memberID})
    row = res.fetchone()
    if row is None :
       return print("\n","Member doesn't exist".center(50,'*'))
    #else :
    #   print("Found member = ", row[0])
    
    res = cur.execute("SELECT book_item_id FROM books_inventory where book_id = :bookid AND status = 0",{"bookid":bookID})
    row = res.fetchall()
    bookItemId = None
    if row is None or len(row) == 0:
       return print("\n","Book copy not available".center(50,'*'))
    else :
       #print("Copies Available = ", len(row))
       bookItemId = row[0][0]
       #for item in row:
       #   print("book item", item[0])
    
       #print("Book item ID", bookItemId)
    
    res = cur.execute("SELECT date('now', '+5 day') ")
    row = res.fetchone()
    duedate = row[0]
    #print("Due date: ", duedate)    
        
    #cur.execute("INSERT INTO book_checkout (book_item_id , member_id , due_date)  \
    #             VALUES (?, ?, ?)", (bookItemId, memberID, duedate))
    cur.execute("INSERT INTO book_checkout (book_item_id , member_id , due_date)  \
                  VALUES (:itemid, :memid, :ddate)", {"itemid":bookItemId, "memid":memberID, "ddate":duedate})
                 
    print("Book borrowed: Due Date ==> ", duedate)
    cur.execute("UPDATE books_inventory \
                 SET status = 1 \
                 WHERE book_item_id = :itemid", {"itemid":bookItemId})
    conn.commit()

def add_book_by_bookname(bookName, bookAuth, bookDesc, numOfCopies, conn):
    #print(" Adding book ", bookName, " with ", numOfCopies, " copies to the library")
    bookName = bookName.rstrip()
    if len(bookName) == 0 :
        print("Can not add book without name")
        return
    
    cur = conn.cursor()
    
    #check if the book already exists
    res = cur.execute("SELECT book_id FROM books_catalog where book_name = :bookNm", {"bookNm":bookName})
    row = res.fetchone()
    if row is None or len(row) ==0:       
         cur.execute("INSERT INTO books_catalog (book_name, book_auth, book_desc)  \
               VALUES (?, ?, ?)", (bookName, bookAuth, bookDesc))
         bookID = cur.lastrowid           
         print(" --> Added book ", bookName, "to catalog. ID of this book = ", bookID)
    else :
         bookID = row[0]
         print (" *** Book ", bookName, " already exists in the library Catalogue *** \n")   
        
    status = 0
    if numOfCopies <= 1 :
        numOfCopies = 1
        
    #print("\n Adding ", numOfCopies ," copies to the inventory ....")    
    while numOfCopies >= 1:
        cur.execute("INSERT INTO books_inventory (book_id, status)  \
               VALUES (?, ?)", (bookID, status))
        bookCopy = cur.lastrowid
        #print ("Added copy ", bookCopy)
        numOfCopies -= 1  
    else :
        print(" Book added to library. Now you can borrow. Happy reading !!!")        
    conn.commit()   

def add_member(fName, lName, email, phone, conn):
    firstName = fName.rstrip()
    lastName = lName.rstrip()
    emailMem = email.rstrip()
    phoneMem = phone.rstrip()
    
    if len(firstName) == 0 or len(lastName) == 0 or len(emailMem) == 0 or len(phoneMem) == 0 :
        print("Can not add member, all inputs are mandatory")
        return
    
    cur = conn.cursor()
    
    res = cur.execute("SELECT member_id FROM members where phone = :phonem", {"phonem":phoneMem})
    row = res.fetchone()
    if row is None or len(row) ==0:
         cur.execute("INSERT INTO members (first_name, last_name, email, phone, status)  \
               VALUES (?, ?, ?, ?, 1)", (firstName, lastName, emailMem, phoneMem))
         memID = cur.lastrowid           
         print("\n --> Added member ", firstName, ". ID of this member = ", memID)
    else :
         memID = row[0]
         print ("\n *** Member ", memID, "with Phone = ", phoneMem, "and Name = ", firstName, " ", lastName, " already exists in the library Catalogue *** \n")
    conn.commit()
    
def list_books_by_member(memid, conn):
    memID = memid.rstrip()
    if len(memID) == 0 :
        print(" Need a non-zero member id")
        return
    
    cur = conn.cursor()
    res = cur.execute("SELECT member_id FROM members where member_id = :memid", {"memid":memID})
    row = res.fetchone()
    
    if row is None or len(row) ==0:
        print(" \n *** Member does not exist", memID)
        return
    else:
        res = cur.execute("SELECT bcat.book_name, bc.due_date  \
                       FROM books_inventory bi, book_checkout bc, books_catalog bcat \
                       where bi.book_id = bcat.book_id AND bi.status = 1 \
                       AND bc.book_item_id = bi.book_item_id \
                       AND bc.member_id = :memid", {"memid":memID} ) 
                       
        print("\n\nList of books borrowed and the Due Date as below.")
        print("-".rjust(30,'-'), "   ", "-".ljust(15, '-'))
        print("Book Name".ljust(30,' '), "   ", "Due Date".ljust(15, ' '))
        print("-".rjust(30,'-'), "   ", "-".ljust(15, '-'))

        rows = cur.fetchall()
        for row in rows:
            bookName = row[0]
            dueDate = row[1]
            print(bookName.ljust(30, ' '),"   ", dueDate)
        print("-".rjust(30,'-'), "   ", "-".ljust(15, '-'), "\n\n")    
    
def main():
    database = r"libraryapp.db"
     
    # create a database connection
    conn = create_connection(database)
    
    endProgram = False
    choice = 0
    while not endProgram:
        memberIDTxt = ''
        bookIDTxt = ''
        memberID = 0
        bookID = 0
        bookName = ''
        bookAuth = ''
        bookDesc = ''
        numOfCopies = 0
        
        print("\n=================================================")
        print("Welcome to DAV Library".center(40,' '))
        print("=================================================")
        print("Library Menu:", "\n",
              "1.See book list".ljust(20,' '),
              "2.Borrow a book".ljust(20,' '),
              "3.Return a book".ljust(20,' '), "\n", 
              "4.Add a book".ljust(20,' '), 
              "5.Add Member".ljust(20,' '), 
              "6.List books by Member".ljust(20,' '), "\n",
              "9.Exit\n")
        choice = input("Enter your Choice [1 | 2 | 3 | 4 |5 |6 | 9 ] = ")
        #print("you chose ---->", choice)
        if choice == '9' :
           print("---> Exiting <---- \n")
           endProgram = True          
        elif choice == '1' :
           get_all_books_inventory(conn)
        elif choice == '2' :
           memberIDTxt = input("What is your member ID? ")
           bookIDTxt = input("What is the Book ID you want to borrow? ")
           #print ("Member ", memberIDTxt, " is borrowing book with ID =  ", bookIDTxt)
           memberID = int(memberIDTxt)
           bookID = int(bookIDTxt)
           borrow_book_by_book_id(bookID, memberID, conn)
        elif choice == '3' :
           memberIDTxt = input("What is your member ID? ")
           bookIDTxt = input("What is the Book ID you want to return? ")
           print ("Member ", memberIDTxt, " is borrowing book with ID =  ", bookIDTxt)
           memberID = int(memberIDTxt)
           bookID = int(bookIDTxt)
           return_book_by_book_id(bookID, memberID, conn)
        elif choice == '4' :
            #print("====> Adding a new book in library ")
            bookName = input(" Enter name of the book = ")
            bookAuth = input (" Name of the Author = ")
            bookDesc = input (" Short description of the book =  ")
            numCopies = input (" How many copies ? ")
            numOfCopies = int(numCopies)
            add_book_by_bookname(bookName, bookAuth, bookDesc, numOfCopies, conn)
        elif choice == '5' :
            fName = input(" Enter Memeber - First Name = ")
            lName = input(" Enter Member - Last Name = ")
            email = input(" Enter email id (format: a@b.com)")
            phone = input(" Enter Phone number (10 digit)")
            add_member(fName, lName, email, phone, conn)
        elif choice == '6' :
            memid = input(" Enter Member ID = ")
            list_books_by_member(memid, conn)
        else :
           print("\nIncorrect choice / choice not available")        
        
    conn.close()    

if __name__ == "__main__":
    #print("Connecting to DB")
    main()