.. _tokens:

Magic Tokens
============

Magic tokens are text snippets that start with the characters sequence ``%!``
and end with the character sequence ``!%``. 

Inbetween are datum point names which may include alternative form specifiers 
seperated by ``As``.

Currently the following magic tokens are supported: 

*Note: magic tokens and rules are case sensitive.* 

.. code::

   OrgName:
      OrgNameAsEntered
      OrgNameAsCleaned
      OrgNameAsUppercase
      OrgNameAsLowercase
      OrgNameAsID
      OrgNameAsUppercaseID
      OrgNameAsLowercaseID
      OrgNameAsUppercaseIDSep
      OrgNameAsLowercaseIDSep
      OrgNameAsAbbreviation
      OrgNameAsInitials

   PluginName:
      PluginNameAsEntered
      PluginNameAsCleaned
      PluginNameAsUppercase
      PluginNameAsLowercase
      PluginNameAsID
      PluginNameAsUppercaseID
      PluginNameAsLowercaseID
      PluginNameAsUppercaseIDSep
      PluginNameAsLowercaseIDSep
      PluginNameAsAbbreviation
      PluginNameAsInitials

   DateTime:
      DateTimeAsIso
      DateTimeAsLocale

   AuthorName:
      AuthorNameAsEntered
      AuthorNameAsCleaned
      AuthorNameAsUppercase
      AuthorNameAsLowercase
      AuthorNameAsID
      AuthorNameAsUppercaseID
      AuthorNameAsLowercaseID
      AuthorNameAsUppercaseIDSep
      AuthorNameAsLowercaseIDSep
      AuthorNameAsAbbreviation
      AuthorNameAsInitials

   Time:
      TimeAsEnglishSeparated
      TimeAsEnglish
      TimeAsLocaleSeparated
      TimeAsLocale
      TimeAsSecondsSinceEpoch

   Date:
      DateAsIsoSeparated
      DateAsIso
      DateAsEnglishDashSeparated
      DateAsEnglishSeparated
      DateAsEnglish
      DateAsLocaleSeparated
      DateAsLocale
      DateAsNameOfDay
      DateAsShortNameOfDay

   ID:
      IDAsEntered


