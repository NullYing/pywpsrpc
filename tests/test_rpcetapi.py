#!/usr/bin/env python3

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) + "/../build")

from pywpsrpc.rpcetapi import etapi
from pywpsrpc import (rpcetapi, common)
from pywpsrpc.utils import RpcIter, RpcProxy


class TestRpcEtApi(unittest.TestCase):

    def setUp(self):
        super().setUp()
        _, self.rpc = rpcetapi.createEtRpcInstance()
        _, self.app = self.rpc.getEtApplication()

    def tearDown(self):
        self.app.Quit()
        super().tearDown()

    def check_call(self, funcName, hr, value=None):
        self.assertEqual(hr, common.S_OK, funcName)

    def test(self):
        hr, pid = self.rpc.getProcessPid()
        self.check_call("rpc.getProcessPid", hr, pid)

        hr, workbooks = self.app.get_Workbooks()
        self.check_call("app.get_Workbooks", hr, workbooks)

        hr, workbook = workbooks.Add()
        self.check_call("workbooks.Add", hr, workbook)

        hr, sheet = workbook.get_ActiveSheet()
        self.check_call("workbook.get_ActiveSheet", hr, sheet)

        hr, rg = sheet.get_Range("A1")
        self.check_call("sheet.get_Range", hr, rg)

        hr = rg.put_Value(RHS="test")
        self.check_call("rg.put_Value", hr)

        rg = sheet.Range("A1")
        self.assertEqual(rg.Value, "test")

        hr, window = self.app.get_ActiveWindow()
        self.check_call("app.get_ActiveWindow", hr, window)

        hr, winType = window.get_Type()
        self.check_call("window.get_Type", hr, winType)

        props = workbook.CustomDocumentProperties
        for prop in RpcIter(props):
            self.assertIsNotNone(prop.Name)

        props = workbook.BuiltinDocumentProperties
        for prop in RpcIter(props):
            self.assertIsNotNone(prop.Name)

        hr = workbook.Close(False)
        self.check_call("workbook.Close", hr)

    def test_pagesetup(self):
        _, workbook = self.app.Workbooks.Add()
        ps = workbook.ActiveSheet.PageSetup
        self.assertEqual(ps.Pages.Count, 0)

        ps.FitToPagesTall = True
        self.assertTrue(ps.FitToPagesTall)

        ps.FitToPagesWide = False
        self.assertFalse(ps.FitToPagesWide)

        workbook.Close(False)

    def test_querytable(self):
        _, workbook = self.app.Workbooks.Add()
        sheet = workbook.ActiveSheet
        self.assertEqual(sheet.QueryTables.Count, 0)
        workbook.Close(False)

    def test_formatcondition(self):
        _, workbook = self.app.Workbooks.Add()
        sheet = workbook.ActiveSheet
        rg = sheet.Range("A1")

        fc = rg.FormatConditions
        hr, cond = fc.AddAboveAverage()

        self.assertEqual(fc.Count, 1)
        self.assertIsNotNone(fc[1])

        cond.AboveBelow = etapi.xlAboveAverage
        self.assertEqual(cond.AboveBelow, etapi.xlAboveAverage)

        workbook.Close(False)

    def test_charts(self):
        _, workbook = self.app.Workbooks.Add()
        self.assertEqual(workbook.Charts.Count, 0)
        workbook.Close(False)

    def test_autofill(self):
        _, workbook = self.app.Workbooks.Add()
        sheet = workbook.ActiveSheet
        rg = sheet.Range("A1")
        rg.put_Value(RHS="1")

        rg = sheet.Range("A2")
        rg.put_Value(RHS="2")

        sourceRg = sheet.Range("A1:A2")
        fillRg = sheet.Range("A1:A20")
        hr, _ = sourceRg.AutoFill(fillRg)
        self.assertEqual(hr, common.S_OK)
        workbook.Close(False)

    def test_shapes(self):
        workbook = RpcProxy(self.app.Workbooks.Add())
        shapes = workbook.ActiveSheet.Shapes
        line = shapes.AddLine(10, 10, 250, 250).Line
        self.assertNotEqual(line, None)
        self.assertEqual(1, shapes.Count)

        line.DashStyle = etapi.msoLineDashDotDot

        for shape in shapes:
            self.assertEqual(shape.Type, etapi.msoLine)
            self.assertEqual(shape.Line.DashStyle, etapi.msoLineDashDotDot)

        workbook.Close(False)

    def test_array(self):
        _, workbook = self.app.Workbooks.Add()
        sheet = workbook.ActiveSheet
        sheet.Range("A1:B1").Value = [1, "a"]
        self.assertEqual(sheet.Range("A1").Value, 1)
        self.assertEqual(sheet.Range("B1").Value, "a")

        value = sheet.Range("A1:B1").Value
        self.assertTrue(isinstance(value, list))
        self.assertTrue(len(value) == 1)
        self.assertEqual(value[0][0], 1)
        self.assertEqual(value[0][1], "a")

        # FIXME: maybe et doesn't support 2-d array???
        sheet.Range("A2:B3").Value = [[2, 3], [4, 5]]
        value = sheet.Range("A2:B3").Value
        self.assertEqual(len(value), 2)
        #self.assertEqual(value[1][1], 5)

        workbook.Close(False)


if __name__ == "__main__":
    unittest.main()
