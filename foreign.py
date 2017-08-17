import xml.etree.ElementTree as ET
import sys

class LocalTable:
    def __init__(self, localTable):
        self.localTable = localTable
        self.foreignTableEntries = set()

    def addForeignTableEntry(self, foreignTableEntry):
        self.foreignTableEntries.add(foreignTableEntry)

    def getForeignTableEntries(self):
        return self.foreignTableEntries


class ForeignTableEntry:
    def __init__(self, foreignTableEntry):
        self.foreignTableEntry = foreignTableEntry
        self.localEntry = ""
        self.foreignEntry = ""

    def setEntry(self, localEntry, foreignEntry):
        self.localEntry = localEntry
        self.foreignEntry = foreignEntry

    def getEntry(self):
        return self.localEntry, self.foreignEntry


def constructTables(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    tables = set()
    for t in root.iter('table'):
        localTable = LocalTable(t.attrib['name'])
        for f in t.iter('foreign-key'):
            foreignTableEntry = ForeignTableEntry(f.attrib['foreignTable'])
            for r in f.findall('reference'):
                foreignTableEntry.setEntry(r.attrib['local'], r.attrib['foreign'])
            localTable.addForeignTableEntry(foreignTableEntry)
        tables.add(localTable)
    return tables


def compareTables(new_tables, old_tables):
    old = set()
    new = set()
    for old_table in old_tables:
        old.add(old_table.localTable)
    for new_table in new_tables:
        new.add(new_table.localTable)
    return old == new


def findTableByName(name, tables):
    for table in tables:
        if table.localTable == name:
            return table

def findEntryByName(name, table):
    for entry in table.foreignTableEntries:
        if entry.foreignTableEntry == name:
            return entry


def compareTable(new_table, old_table):
    if new_table.localTable != old_table.localTable:
        raise AssertionError("The name of new table and old table should be the same")
    old = set()
    new = set()
    for entry in new_table.getForeignTableEntries():
        new.add(entry.foreignTableEntry)
    for entry in old_table.getForeignTableEntries():
        old.add(entry.foreignTableEntry)
    return old - new


def compareEntry(new_entry, old_entry):
    # if not new_entry.getEntry() == old_entry.getEntry():
    #     print(new_entry.getEntry())
    #     print(old_entry.getEntry())
    #     return False
    # return True
    return new_entry.getEntry() == old_entry.getEntry()


def tableDiff(new_tables, old_tables):
    rtn = True
    if not compareTables(new_tables, old_tables):
        print("Table names do not compatible between two xml files")
        rtn = False
    else:
        for table in new_tables:
            table_name = table.localTable
            new_table = table
            old_table = findTableByName(table_name, old_tables)
            if compareTable(new_table, old_table) != set():
                print("Foreign key is different in table: " + table_name)
                rtn = False
            else:
                for entry in new_table.getForeignTableEntries():
                    entry_name = entry.foreignTableEntry
                    new_entry = entry
                    old_entry = findEntryByName(entry_name, old_table)
                    if not compareEntry(new_entry, old_entry):
                        print("Foreign key's entry names are different in table: " + "\"" + table_name + "\"" + " with foreign key name of", entry_name)
                        rtn= False
    return rtn


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python foreign.py new.xml old.xml")
        exit(-1)
    print("Running " + str(sys.argv[0]) + "...")
    filename_1 = sys.argv[1]
    filename_2 = sys.argv[2]
    new_tables = constructTables(filename_1)
    old_tables = constructTables(filename_2)
    if not tableDiff(new_tables, old_tables):
        print("---- Difference Occurred")
    else:
        print("---- No difference in aspect of Foreign Key")