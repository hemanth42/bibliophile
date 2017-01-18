####################################

"""
Bibliophile v0.1

Written By Hemanth. A

All Rights Reserved - Released Under GPL License

A Bookmanager application written for bibliophiles by a bibliophile!

-----------------------------------
NOTE: WHEN freezing using build_exe

add 'from PySide import QtXml'

AND, Change .py to .pyw
------------------------------------

"""



###################################

from PySide import QtCore, QtGui, QtUiTools, QtXml

#import MySQLdb
import sqlite3

import sys

import time

import random

import os
import shutil
import ntpath

class App():

    # CONSTRUCTOR THAT INITIALIZES APP and Loads MainUI
    def __init__(self):
        #super(App, self).__init__()
        self.loadMainUI()
        #self.DB('test')




    #MAIN UI FUNCTION
    def loadMainUI(self):

        self.ui = self.loadUiWidget("gui.ui")
        self.ui.setWindowTitle("Bibliophile v0.5 Beta")
        self.ui.show()
        self.ui.showMaximized()

        import ctypes
        myappid = u'Bibliophile' # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        self.ui.table.setColumnHidden(0, 1) # Hiding the bookid column in the table

        self.DBops('get')   # Initial Load the database data into the table first

       #-- POPULATE BOOK DETAILS IN SIDE BAR VIEW FUNCTION ---------------
        def populate_book_details(initial=0):

            if initial == 1:
                current_row = 0
                self.DBops('getcomment',initial=0)
            else:
                current_row = self.ui.table.currentRow()
                self.DBops('getcomment')

            self.ui.titlelabel.setText("Title : " + self.ui.table.item(current_row, 1).text())
            self.ui.authorlabel.setText("Author : " + self.ui.table.item(current_row, 2).text())
            ratingx = self.ui.table.item(current_row, 3).text()
            self.ui.ratinglabel.setText("Rating : " + ratingx[len(ratingx)-5:len(ratingx)])
            self.ui.tagslabel.setText("Tags : " + self.ui.table.item(current_row, 4).text())

            #Book Cover
            book_id = self.ui.table.item(current_row, 0).text()
            pixmap = QtGui.QPixmap("covers/cover" + book_id)

            self.ui.label_2.setPixmap(pixmap)
            self.ui.label_2.show()

        populate_book_details(1)  # Populating book details on initial run, take first row data
        self.ui.table.itemSelectionChanged.connect(populate_book_details) #This singal is activated when any cell is selected

        def setClose():
            MainApp.setQuitOnLastWindowClosed(1)


        #------------- ADD/UPDATE BOOK FORM FUNCTION --------------------------------------------
        def showAddBook(mode=None):
            addform = self.loadUiWidget("addbook.ui", param='child')

            addform.show()

            ### KILLED TWO BIRDS WITH ONE STONE BY REMOVING PARENT PROPERY - APP closes without any problem, dialogs don't interfere

            if mode == 'edit':
                addform.pushbookbtn.setText("Save Changes")
                addform.setWindowTitle("Edit Book")
                current_row = self.ui.table.currentRow()
                book_idx = self.ui.table.item(current_row,0).text()
                addform.titlebox.setText(self.ui.table.item(current_row,1).text())
                addform.authorbox.setText(self.ui.table.item(current_row,2).text())
                addform.tagsbox.setText(self.ui.table.item(current_row,4).text())
                ratingxx = self.ui.table.item(current_row,3).text()
                addform.ratingslider.setValue(int(ratingxx[len(ratingxx)-4:len(ratingxx)-3]))
                commentx = self.DBops("getcomment",mode='edit')
                addform.commentsbox.setText(commentx)
                #print(book_id)
                pixmapx = QtGui.QPixmap("covers/cover"+book_idx)
                addform.cover.setPixmap(pixmapx)


            #OPEN BOOK COVER AND RETRIVE FILE NAME
            def CoverDialog():
                addform.fileName = QtGui.QFileDialog.getOpenFileName(None,'Choose Book Cover', '/', selectedFilter='*.png')
                if addform.fileName:
                    pixmap = QtGui.QPixmap(addform.fileName[0])
                    addform.cover.setPixmap(pixmap)


            #BOOK COVER BTN HANDLER
            addform.cover_btn.clicked.connect(CoverDialog)

            #--- VALIDATE AND PUSH CONTENT INTO DATABASE
            def validateAndPush():
                val_list = {}
                title = addform.titlebox.text()
                author = addform.authorbox.text()
                tags = addform.tagsbox.text()
                rating = addform.ratingslider.value()
                comments = addform.commentsbox.toPlainText()
                if len(title) < 2 : self.showMsg("Enter The Title Of The Book!"); val_list['t'] = 0;
                else: val_list['t'] = 1

                if len(author) < 2 : self.showMsg("Enter The Name Of The Author!"); val_list['a'] = 0;
                else: val_list['a'] = 1

                if len(tags) < 2 : self.showMsg("Enter The Tags!"); val_list['tg'] = 0;
                else: val_list['tg'] = 1

                if val_list['t'] == 1 and val_list['a'] == 1 and val_list['tg'] == 1  :
                    print("Everything Seems to be in Order!")
                    if mode == 'edit':
                        self.DBops("update",bookid=book_idx,title=title,author=author,tags=tags,rating=rating,comment=comments)
                        print("Your Book Has Been Updated!")
                        rand_id = book_idx
                    else:
                        rand_id = self.DBops("add",title=title,author=author,tags=tags,rating=rating,comment=comments)
                        print("Your Book Has Been Added!")
                    #------ copy and rename ----
                    cover_change = 0
                    if hasattr(addform, 'fileName'):
                        src_file = addform.fileName[0]
                    else:
                        cover_change = 1

                    if cover_change == 1:
                        pass
                    else:
                        dest_path = "covers"
                        shutil.copy(src_file,dest_path)
                        base_name = ntpath.basename(src_file)
                        print(base_name)
                        shutil.move("covers/"+base_name,"covers/cover"+str(rand_id))
                    addform.close()
                    #del addform
                    self.ui.table.clearContents()
                    self.DBops('get')


            # PUSH BOOKS INTO DB BTN HANDLER
            addform.pushbookbtn.clicked.connect(validateAndPush)

        # ADD BTN CLICK EVENT HANDLER - OPENS FORM
        self.ui.add_btn.clicked.connect(showAddBook)

        #----------- DELETE BOOK FUNCTION -------------------------------------
        def deleteBook():
            current_row = self.ui.table.currentRow()
            book_id = int(self.ui.table.item(current_row,0).text())
            print(book_id)
            self.DBops('delete',bookid=book_id)
            fname = "covers/cover"+str(book_id)
            if os.path.isfile(fname):
                os.remove(fname)
            else:
                pass
            print("Book has been deleted")
            self.ui.table.clearContents()
            self.DBops('get')
            #populate_book_details(initial=1)
        self.ui.delbtn.clicked.connect(deleteBook)



        #------------- UPDATE BOOK FUNCTION ------------------------------------

        def edit_test():
            #self.DBops("update",bookid=5622,title="YEAH!!!",author="OG!!!",rating=2,tags="ssup yo yo",comment='honey')
            showAddBook(mode='edit')
        self.ui.editbtn.clicked.connect(edit_test)


        #-------------- FULL SCREEN FUNCTION ----------------------------------
        self.ui.full_screen = 0
        def setFullScreen():
            if self.ui.full_screen != 1:
               self.ui.showFullScreen()
               self.ui.full_screen = 1
            else:
                self.ui.showMaximized()
                self.ui.full_screen = 0

        self.ui.fullscreenbtn.clicked.connect(setFullScreen)

        #------------- ABOUT FUNCTION -------------------------------------------

        def show_about():
            self.showMsg("""<center> <h3> Bibliophile v0.5 Beta </h3>  <img src = 'icons/book_icon.png'> </center> <br> <p> Written By Hemanth.A </p> <p> All Rights Reserved, Released Under GPL </p> <p> An ultra simple bookmanager made by a <u> bibliophile </u> for other <u> bibliophiles </u> </p>""")
        self.ui.aboutbtn.clicked.connect(show_about)

        
        


    # FUNCTION THAT PARSES .UI XML FILE AND RETURNS OBJECT
    def loadUiWidget(self, uifilename, param=None):
        loader = QtUiTools.QUiLoader()
        uifile = QtCore.QFile(uifilename)
        uifile.open(QtCore.QFile.ReadOnly)
        if param == 'child':
            ui = loader.load(uifile, self.ui)
        else:
            ui = loader.load(uifile)   #ui = loader.load(uifile, self) -- This is the old line, I removed 'self' to remove parent
        uifile.close()             # So that my mainwindow will be independant in the taskbar
        return ui

    # FUNCTION FOR ALL DATABASE RELATED OPERATIONS
    def DBops(self,param=None, initial = 0, mode = None, **kwargs):

        try:
            #conn = MySQLdb.connect("localhost","root","",db)
            conn = sqlite3.connect('library')
            db = conn.cursor()


            #---------------------------------------------------

            if param == 'test':
                pass


            # GET BOOKS FROM DB AND LOAD INTO TABLE
            if param == 'get':
                db.execute("SELECT * FROM `books_table`")
                rows = db.fetchall()
                self.ui.table.setRowCount(len(rows))
                #self.ui.table.setColumnCount(4)
                row_count = 0
                for row in rows:                      # Main loop to retrieve row by row data from books_table

                     x = 0
                     rating = ""
                     for x in range(0,int(row[3])):    # Nice loop to take rating value from DB and turn it into stars
                         rating = rating + "  " + '*'
                         x = x + 1

                     bookid = str(row[0])
                     title = row[1]
                     author = row[2]
                     tags = row[4]
                     #comments = row[5]

                     self.bookid_row = QtGui.QTableWidgetItem(str(bookid))  #Invisible Bookid
                     self.ui.table.setItem(row_count, 0, self.bookid_row)

                     self.title_row = QtGui.QTableWidgetItem(title)
                     self.ui.table.setItem(row_count, 1, self.title_row)

                     self.author_row = QtGui.QTableWidgetItem(author)
                     self.ui.table.setItem(row_count, 2, self.author_row)

                     self.rating_row = QtGui.QTableWidgetItem(rating + " (" + str(row[3]) + "/6)")
                     self.ui.table.setItem(row_count, 3, self.rating_row)

                     self.tags_row = QtGui.QTableWidgetItem(tags)
                     self.ui.table.setItem(row_count, 4, self.tags_row)

                     row_count = row_count + 1
                     
                #self.ui.table.setColumnHidden(0, 1) # To Hide any column(useful to hide bookid in db used in sql queries)

            # ADD BOOK OPERATION
            elif param == 'add':
                if(kwargs['title'] and kwargs['author'] and kwargs['tags'] and kwargs['comment'] and kwargs['rating'] is not None):
                    rand_id = int( str(random.randint(11,99)) + str(random.randint(11,99)) )
                    db.execute("""INSERT INTO books_table (bookid, title, author, rating, tags, comment) VALUES('{}','{}','{}','{}','{}','{}')""".format(rand_id, kwargs['title'], kwargs['author'], kwargs['rating'], kwargs['tags'], kwargs['comment']))
                    conn.commit()
                    return rand_id

            # UPDATE BOOK OPERATION
            elif param == 'update':
                if(kwargs['bookid'] and kwargs['title'] and kwargs['author'] and kwargs['tags'] and kwargs['comment'] and kwargs['rating'] is not None):
                    db.execute("""UPDATE books_table SET title ='{0}', author ='{1}', rating ='{2}', tags ='{3}', comment='{4}' WHERE bookid = {5} """.format(kwargs['title'], kwargs['author'], kwargs['rating'], kwargs['tags'], kwargs['comment'], str(kwargs['bookid'])))
                    conn.commit()


            # DELETE BOOK OPERATION
            elif param == 'delete':
                book_id = kwargs['bookid']
                db.execute("DELETE FROM `books_table` WHERE bookid = " + str(book_id))
                conn.commit()

            # LOAD COMMENT FOR CURRENT SELECTED BOOK IN ROW AND SHOW IN SIDEBAR VIEW
            elif param == 'getcomment':
                if initial == 1:
                    current_row = 0
                else:
                    current_row = self.ui.table.currentRow()             # Get current row

                #item(row,column) returns object.
                #item(row,column).text() returns text of that item(bookid invisible column in this case)
                book_id = self.ui.table.item(current_row, 0).text()
                db.execute("SELECT * FROM `books_table` WHERE bookid = " + str(book_id)) #Passing bookid from invisible column
                comment_txt = db.fetchone()[5]
                if mode == 'edit':
                    return comment_txt
                else:
                    self.ui.commentslabel.setText(comment_txt)

        except:
            pass


    def showMsg(self,param = ' '):
        box = QtGui.QMessageBox(parent=self.ui)
        box.setWindowTitle("Hello There!")
        box.setText(param)
        box.resize(100,100)
        box.exec_()

def init():
    QtCore.QCoreApplication.addLibraryPath('plugins') # This line adds the much needed JPEG Support to QPixMap
    import qdarkstyle
    global MainApp
    MainApp = QtGui.QApplication(sys.argv)
    MainApp.setStyleSheet(qdarkstyle.load_stylesheet())
    #MainApp.setQuitOnLastWindowClosed(0)
    #MainApp.setStyle("Plastique")
    #print(QtGui.QStyleFactory.keys())

    # RANDOM SPLASH SCREEN IMAGE SHOWN AT APP STARTUP
    #Cheeky Little Splash Screen
    rand = random.randint(1,6)
    splash_pix = QtGui.QPixmap('imgs/splash' + str(rand))
    splash = QtGui.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()


    # TIME FOR SPLASH SCREEN IMAGE TO STAY ON
    splash.finish(time.sleep(2))
    a = App()
    MainApp.exec_()




init()






