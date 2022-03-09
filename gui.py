import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

form_class1 = uic.loadUiType("result.ui")[0]


class WindowClass(QMainWindow, form_class1):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.cmb_region.currentIndexChanged.connect(self.cmbRegionFunction)
        self.cmb_rent.currentIndexChanged.connect(self.cmbRentFunction)
        self.cmb_room.currentIndexChanged.connect(self.cmbRoomFunction)

        self.closeButton.clicked.connect(self.closeButtonFunction)
        self.okButton.clicked.connect(self.okButtonFunction)

    def closeButtonFunction(self):
        self.close()

    def okButtonFunction(self):
        df1 = pd.read_excel('data2.xlsx', sheet_name = 'all')
        df2 = pd.read_excel('data.xlsx', sheet_name = 'all')

        if (self.dong == '서천'):
            self.dong = 'seocheon'
        elif (self.dong == '영통'):
            self.dong = 'youngtong'

        if (self.rent == '전세'):
            self.rent = 'lease'
        elif (self.rent == '월세'):
            self.rent = 'monthly'

        self.roomNumber = self.roomNumber[:]

        tmp1 = df1[df1.동 == self.dong]
        tmp1 = tmp1[tmp1.임대 == self.rent]
        tmp1 = tmp1[tmp1.방수 == self.roomNumber]

        tmp2 = df2[df2.동 == self.dong]
        tmp2 = tmp2[tmp2.임대 == self.rent]
        self.roomNumber = int(self.roomNumber[0])
        tmp2 = tmp2[tmp2.방수 == self.roomNumber] # self.roomNumber == 1

        items_df1 = []
        items_df2 = []
        items = []
        df1_values = tmp1.values #recommend 출력 할 때
        df2_values = tmp2.values #recommend
        print('*******', df2_values)

        for i in range(len(df1_values)):
            recommText = ''
            recomm = []
            recommText += str(df1_values[i][1]) + '      '
            for j in range(3, 8):
                recommText += str(df1_values[i][j]) + '      '
            recommText += str(df1_values[i][8])
            for j in [1, 3, 4, 5, 6, 7, 8]:
                recomm.append(df2_values[i][j])
            items.append(recommText)
            items_df1.append(recommText.split('      '))
            items_df2.append(recomm)

        print(items_df1)
        print(items_df2)

        if(items != []):
            text = '\n\n\n\t\t' + self.dong + ' ' + self.rent + '\t매물을 선택하세요.\n\n\n\t[매물번호  가격  층  방수  욕실수  단층/복층  중개수수료]\n\n\n'
            item, ok = QInputDialog.getItem(self, 'Select', text, items, 0, False)
            if ok and item:
                print(item)
                item = item.split('      ')
                self.selec = '\t매물번호 ' + item[0] + '\n'
                print(item)
                self.num = int(item[0])
                tmp_df2 = df2.loc[df2.매물번호 == self.num].values
                print(tmp_df2)
                self.itemFloor = tmp_df2[0][4]

                self.itemRoomNumber = tmp_df2[0][5]

                self.itemBathroom = tmp_df2[0][6]

                self.itemStoried = tmp_df2[0][7]

                self.itemPay = tmp_df2[0][8]

                self.itemPrice = tmp_df2[0][3]

                print(self.num, self.itemPrice, self.itemFloor, self.itemRoomNumber, self.itemBathroom, self.itemStoried, self.itemPay)
                self.predictFunction()
                tmpText = ''
                for i in range(len(items_df2)):
                    diff = self.newPred - int(items_df2[i][1])
                    if (diff >= 0):
                        for j in range(len(items_df1[i])):
                            tmpText += str(items_df1[i][j]) + '  '
                        tmpText += '\n'
                self.recomm.setText(tmpText)
        else:
            self.label.setText('해당 조건에 맞는 매물이 없습니다.')

    def predictFunction(self):
        df = pd.read_excel('data.xlsx', sheet_name = 'all')

        # seocheon: 0, youngtong: 1  /  lease:0, monthly:1
        for i in range(len(df)):
            if (df.iloc[i, 0] == 'seocheon'):
                df.iloc[i, 0] = 0
            else:
                df.iloc[i, 0] = 1

            if (df.iloc[i, 9] == 'lease'):
                df.iloc[i, 9] = 0
            else:
                df.iloc[i, 9] = 1

        if self.dong == 'seocheon':
            self.dong = 0
        else:
            self.dong = 1

        if self.rent == 'lease':
            self.rent = 0
        else:
            self.rent = 1

        X = df[['동', '임대', '방수', '중개수수료']]
        y = df['가격']

        lr = LinearRegression(fit_intercept = True, normalize = True, n_jobs = None)
        lr.fit(X, y)
        self.newPred = lr.predict([[self.dong, self.rent, self.itemRoomNumber, self.itemPay]])
        self.newPred = int(self.newPred[0])
        print('예측 가격: ', self.newPred, ',   실제 가격: ', self.itemPrice)
        diff = self.newPred - self.itemPrice
        tmp = self.selec
        if diff > 0:
            tmp += '예측 가격보다 ' + str(diff) + '원 저렴합니다.'
            self.label.setText(tmp)
        elif diff < 0:
            tmp += '예측 가격보다 ' + str(-diff) + '원 비쌉니다.'
            self.label.setText(tmp)
        else:
            tmp += '예측 가격과 동일합니다.'
            self.labelsetText(tmp)

    def cmbRegionFunction(self):
        # self.region.setText(self.cmb_region.currentText())
        self.dong = self.cmb_region.currentText()
        print(self.dong)

    def cmbRentFunction(self):
        self.rent = self.cmb_rent.currentText()
        print(self.rent)

    def cmbRoomFunction(self):
        self.roomNumber = self.cmb_room.currentText()
        print(self.roomNumber)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()