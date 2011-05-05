# import platform
# this line shouldn't be read as it is a comment
# import import <-- shouldn't count as init import
#bogus entry
r'\$\{YEAR\}' = time.strftime('%Y')
r'\$\{DATE\}' = time.strftime('%Y-%m-%d')
r'\$\{FULLNAME\}' = u'André Berg'
r'\$\{ORGANIZATION_NAME\}' = 'Berg Media'
r'\$\{LICENSE\}' = "# Licensed under the Apache License, Version 2.0 (the \"License\");\n# you may not use this file except in compliance with the License.\n# You may obtain a copy of the License at\n#\n#      http://www.apache.org/licenses/LICENSE-2.0\n#\n# Unless required by applicable law or agreed to in writing, software\n# distributed under the License is distributed on an \"AS IS\" BASIS,\n# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\n# See the License for the specific language governing permissions and"
r'\$\{PROCESSOR_TYPE\}' = platform.processor()
r'\$\{ENCODING\}' = 'utf-8'