from django.shortcuts import render
import csv
from myOpt.models import OptimizationData,FinalData
from datetime import datetime,timedelta
import datetime
from django.http import HttpResponse
import xlsxwriter


#Create your views here.
def readAndWriteData(request):
    OptimizationData.objects.all().delete()
    counter = 0
    csv_file = open('example.csv')
    csv_reader = csv.reader(csv_file, delimiter = ',')
    next(csv_reader)
    objList = []
    for row in csv_reader:
       # d = datetime.date(row[0])
        s = row[0]
        d =datetime.datetime.strptime(s, '%d-%m-%Y').strftime('%Y-%m-%d')
        
        newRow = OptimizationData(date = d, store = row[1],location = row[2],code = row[3],salerProductName = row[4],mainGroup = row[5],subGroup = row[6],productVariety = row[7],salesAmount = row[8])
        objList.append(newRow)
        counter = counter + 1
        if counter % 20 == 0:
            OptimizationData.objects.bulk_create(objList)
            objList = []
       
       
    if objList:
         OptimizationData.objects.bulk_create(objList)
        
    csv_file.close()
    return HttpResponse('finito')
 
def readFromDB(request):
     oldopt = OptimizationData.objects.filter(productVariety = 'cesit-1').order_by('date')
     FinalData.objects.all().delete()
     count = 0
     objlist = []
     for obj in oldopt:
         if count == 0:
             lastDate = obj.date
             lastAmount = obj.salesAmount
         else:
            if lastDate == obj.date:
                obj.salesAmount = lastAmount + obj.salesAmount
                lastObj = obj
            else:
                newEntry = FinalData(date = lastObj.date,salesAmount = lastObj.salesAmount)
                objlist.append(newEntry)
                lastObj = obj
                lastDate = obj.date
                
            if len(objlist) == 20:
                FinalData.objects.bulk_create(objlist)
                objlist = []
         count+= 1   
    
     if objlist:
         FinalData.objects.bulk_create(objlist)
         
     opt = FinalData.objects.all()
     opt2 = FinalData.objects.all()
     workbook = xlsxwriter.Workbook('Expenses03.xlsx')
     worksheet = workbook.add_worksheet('Sheet 1')
     bold = workbook.add_format({'bold': True})
     worksheet.write('A1', 'Date', bold)
     worksheet.write('B1', 'Amount', bold)
    # worksheet.write('A1', 'Gun', bold)
    # worksheet.write('B1', 'Magaza', bold)
    # worksheet.write('C1', 'Lokasyon', bold)
    # worksheet.write('D1', 'Kod', bold)
    # worksheet.write('E1', 'Satici/UrunAdi', bold)
    # worksheet.write('F1', 'AnaGrup', bold)
    # worksheet.write('G1', 'AltGrup', bold)
    # worksheet.write('H1', 'UrunCesidi', bold)
    # worksheet.write('I1', 'SatisMiktari', bold)
# Some data we want to write to the worksheet.

# Start from the first cell. Rows and columns are zero indexed.
     row = 1
     col = 0

# Iterate over the data and write it out row by row.
     for obj in opt:
        worksheet.write(row, col,str(obj.date))
        worksheet.write(row, col + 1, obj.salesAmount)
 #      worksheet.write(row, col + 2, obj.location)
 #      worksheet.write(row, col + 3,str( obj.code))
 #      worksheet.write(row, col + 4, obj.salerProductName)
 #      worksheet.write(row, col + 5, obj.mainGroup)
 #      worksheet.write(row, col + 6, obj.subGroup)
 #      worksheet.write(row, col + 7, obj.productVariety)
 #      worksheet.write(row, col + 8, obj.salesAmount)
        row += 1

# Write a total using a formula.

     chart = workbook.add_chart({'type': 'line'})


# Configure the chart. In simplest case we add one or more data series.
     chart.add_series({
         'values': ['Sheet 1', 0, 1,row-1 ,1],
         'categories' : ['Sheet 1', 1, 0, row-1, 0],
        'line' : {'color': 'blue'},
         'name' : 'Real Amount',
     })
     chart.set_title ({'name': 'Optimization Results'})
     chart.set_x_axis({'name': 'Sales Amount'})
     chart.set_y_axis({'name': 'Date'})
    
     worksheet.insert_chart('K1', chart)
 
     workbook.close()
     return HttpResponse('readFinito')
        
