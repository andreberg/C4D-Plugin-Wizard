.. _forms:

Alternative Forms
=================

The following tables provide an overview over some of the alternative 
forms available. Remember that you can define your own replacements via
the RULES dictionary in your rules.py file.

*Note: magic tokens and rules are case sensitive.* 

Names
-----

===================== ============================ =========================
 Form                  Input                        Output
===================== ============================ =========================
 Abbreviation          Make Super Awesome Button    MSAB (up to 6 letters)
 Initials              Make Super Awesome Button    MSA (up to 3 letters)
 ID                    Make Awesome Button          MakeAwesomeButton
 UppercaseID           Make Awesome Button          MAKEAWESOMEBUTTON
 UppercaseIDSep        Make Awesome Button          MAKE_AWESOME_BUTTON
 Cleaned               "Déjà-vu (_+=?!)"            Deja-Vu (_+=!)
===================== ============================ =========================

Date & Time
-----------

===================== =====================
 Form                  Output
===================== =====================
 Iso                   2013-08-28T16:31:05
 Locale                08/28/13 16:31:05
===================== =====================

Time
----

===================== =====================
 Form                  Output
===================== =====================
 Locale                163105
 LocaleSeparated       16:31:05
 English               043105PM
 EnglishSeparated      04:31:05 PM
 SecondsSinceEpoch     1377700431
===================== =====================

Date
----

======================= =====================
 Form                    Output
======================= =====================
 Iso                     20130828
 IsoSeparated            2013-08-28
 Locale                  082813
 LocaleSeparated         08/28/13
 English                 082813
 EnglishSeparated        08/28/13
 EnglishDashSeparated    08-28-13
 NameOfDay               Wednesday
 ShortNameOfDay          Wed
======================= =====================

