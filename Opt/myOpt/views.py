from django.shortcuts import render
import csv
from myOpt.models import OptimizationData,FinalData
from datetime import datetime,timedelta
import datetime
from django.http import HttpResponse
import xlsxwriter
from numpy.lib.function_base import average
import math

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
     fitCount = 0
     weeklyFit = []
     weekCount = 0
     totalCount = 0
     finalArray = []
     for obj in opt2:
             weeklyFit.append(obj)
             weekCount += 1
             totalCount += 1
             if weekCount == 7 or totalCount == 333:
                total = 0
                for objs in weeklyFit:
                    total += objs.salesAmount
                if weekCount == 7:
                    average = total/7
                else:
                    average = total/5
                for objs in weeklyFit:
                    distance = objs.salesAmount - average
                    finalArray.append(objs.salesAmount - distance/2)
                weekCount = 0
                weeklyFit = []
     fitCount2 = 0
     weeklyFit2 = []
     weekCount2 = 0
     totalCount2 = 0
     finalArray2 = []
     threefit = []
     for obj in opt2:
             weeklyFit2.append(obj)
             weekCount2 += 1
             totalCount2 += 1
             if weekCount2 == 7 or totalCount2 == 333:
                total = 0
                for objs in weeklyFit2:
                    total += objs.salesAmount
                    
                if weekCount2 == 7:
                    average = total/7
                else:
                    average = total/5
                
                fitCount2 = 0
                
                for objs in weeklyFit2:
                    fitCount2+=1
                    average2 = average
                    threefit.append(objs)
                    totalthree = 0
                    if fitCount2 == 3:
                        for objss in threefit:
                             totalthree += objss.salesAmount
                        average2 = totalthree/3
                        threefit = []
                        fitCount2 = 0
                    finalArray2.append(average2)
                weekCount2 = 0
                weeklyFit2 = []
    
     baseArray = []
     predictionArray = []
     totalAverage = 0
     total = 0
     lastMonthAverage = 0
     totalLastMonth = 0
     realArray = []
     monthCount = 0
     monthTurn = 0
     patternArray = []
     febTurn = 0
     totalBaseCount = 0
     for i in range(31):
        patternArray.append(0)
        
     for obj in opt2:
        if totalBaseCount < 258:
            total += obj.salesAmount
        if totalBaseCount < 317:
            if totalBaseCount == 0:
                patternArray[monthCount] = obj.salesAmount
            else:
                patternArray[monthCount] += obj.salesAmount
        if obj.date > datetime.date(2016,12,31) and obj.date < datetime.date(2017,2,1):
            baseArray.append(obj)
            totalLastMonth += obj.salesAmount
            monthTurn = 0
        if obj.date > datetime.date(2017,1,31) and obj.date < datetime.date(2017,3,1):
            realArray.append(obj)
            febTurn = 1    
        monthCount+= 1
        if febTurn == 1 and monthCount == 28:
            monthCount = 0
            monthTurn = 0
            febTurn = 0
        if monthTurn == 0 and monthCount == 31:
            monthCount = 0
            monthTurn = 1
        if monthTurn == 1 and monthCount == 30:
            monthCount = 0
            monthTurn = 0
        totalBaseCount+=1
     for i in range(28):
         patternArray[i] = patternArray[i]/317
     lastMonthAverage = totalLastMonth/31
     totalAverage = total/258
     predictCount = 0
     predictAverage = totalAverage + (lastMonthAverage - totalAverage)/3*4
     predictTotal = predictAverage * 28
     remaining = 0
     while predictCount < 28:
         if predictCount == 0:
             temp = (baseArray[predictCount].salesAmount/5*3 + patternArray[predictCount]/5*2) + lastMonthAverage - totalAverage
             remaining = (baseArray[predictCount].salesAmount/5*3 + patternArray[predictCount]/5*2) - predictAverage
             
         else:
             if remaining > 1:
                temp = (baseArray[predictCount].salesAmount/5*3 + patternArray[predictCount]/5*2) - remaining + lastMonthAverage - totalAverage
                remaining = (baseArray[predictCount].salesAmount/5*3 + patternArray[predictCount]/5*2) - predictAverage
             else:
                temp = (baseArray[predictCount].salesAmount/5*3 + patternArray[predictCount]/5*2) + lastMonthAverage - totalAverage
         
         temp = math.ceil(temp)
         predictionArray.append(temp)
         predictCount+=1      
     workbook = xlsxwriter.Workbook('Expenses055.xlsx')
     worksheet = workbook.add_worksheet('Sheet 1')
     bold = workbook.add_format({'bold': True})
     worksheet.write('A1', 'Date', bold)
     worksheet.write('B1', 'Amount', bold)
     worksheet.write('C1', 'BasicFit', bold)
     worksheet.write('D1', 'RoundFit', bold)
     worksheet.write('E1', 'RealFeb', bold)
     worksheet.write('F1', 'PredictedFeb', bold)
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
     totalCount = 0
     for obj in opt:
        worksheet.write(row, col,str(obj.date))
        worksheet.write(row, col + 1, obj.salesAmount)
        worksheet.write(row, col + 2, finalArray[totalCount])
        worksheet.write(row, col + 3, finalArray2[totalCount])
        if totalCount<28:
            worksheet.write(row, col + 4, realArray[totalCount].salesAmount)
            worksheet.write(row, col + 5, predictionArray[totalCount])
 #      worksheet.write(row, col + 2, obj.location)
 #      worksheet.write(row, col + 3,str( obj.code))
 #      worksheet.write(row, col + 4, obj.salerProductName)
 #      worksheet.write(row, col + 5, obj.mainGroup)
 #      worksheet.write(row, col + 6, obj.subGroup)
 #      worksheet.write(row, col + 7, obj.productVariety)
 #      worksheet.write(row, col + 8, obj.salesAmount)
        row += 1
        if totalCount!=333:
            totalCount+=1
# Write a total using a formula.

     chart = workbook.add_chart({'type': 'line'})


# Configure the chart. In simplest case we add one or more data series.
     chart.add_series({
         'values': ['Sheet 1', 0, 1,row-1 ,1],
         'categories' : ['Sheet 1', 1, 0, row-1, 0],
        'line' : {'color': 'blue'},
         'name' : 'Real Amount',
     })
     chart.add_series({
         'values': ['Sheet 1', 0, 2,row-1 ,2],
         'categories' : ['Sheet 1', 1, 0, row-1, 0],
        'line' : {'color': 'orange'},
         'name' : 'BasicFit',
     })
     chart.set_title ({'name': 'Optimization Results'})
     chart.set_x_axis({'name': 'Sales Amount'})
     chart.set_y_axis({'name': 'Date'})
     
     chart2 = workbook.add_chart({'type': 'line'})


# Configure the chart. In simplest case we add one or more data series.
     chart2.add_series({
         'values': ['Sheet 1', 0, 1,row-1 ,1],
         'categories' : ['Sheet 1', 1, 0, row-1, 0],
        'line' : {'color': 'blue'},
         'name' : 'Real Amount',
     })
     chart2.add_series({
         'values': ['Sheet 1', 0, 3,row-1 ,3],
         'categories' : ['Sheet 1', 1, 0, row-1, 0],
        'line' : {'color': 'orange'},
         'name' : 'roundFit',
     })
     chart2.set_title ({'name': 'Optimization Results2'})
     chart2.set_x_axis({'name': 'Sales Amount'})
     chart2.set_y_axis({'name': 'Date'})
     
     chart3 = workbook.add_chart({'type': 'line'})


# Configure the chart. In simplest case we add one or more data series.
     chart3.add_series({
         'values': ['Sheet 1', 0, 4,28 ,4],
         'categories' : ['Sheet 1', 260, 0, 287, 0],
        'line' : {'color': 'blue'},
         'name' : 'Real Amount',
     })
     chart3.add_series({
         'values': ['Sheet 1', 0, 5,28 ,5],
         'categories' : ['Sheet 1', 260, 0, 287, 0],
        'line' : {'color': 'orange'},
         'name' : 'roundFit',
     })
     chart3.set_title ({'name': 'Optimization Results2'})
     chart3.set_x_axis({'name': 'Sales Amount'})
     chart3.set_y_axis({'name': 'Date'})
     worksheet.insert_chart('K1', chart)
     worksheet.insert_chart('K2', chart2)
     worksheet.insert_chart('K3', chart3)
 
     workbook.close()
     return HttpResponse('readFinito')
        
