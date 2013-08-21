# coding: utf-8
import time

RULES = {
    '${YEAR}': time.strftime('%Y'),
    '${DATE}': time.strftime('%Y-%m-%d'),
    '${FULLNAME}': 'Andre Berg',
    '${ORGANIZATION_NAME}': 'Berg Media',
    '${LICENSE}': "# Licensed under the Apache License, Version 2.0 (the \"License\");\n# you may not use this file except in compliance with the License.\n# You may obtain a copy of the License at\n#\n#      http://www.apache.org/licenses/LICENSE-2.0\n#\n# Unless required by applicable law or agreed to in writing, software\n# distributed under the License is distributed on an \"AS IS\" BASIS,\n# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\n# See the License for the specific language governing permissions and",
    '${ENCODING}': 'utf-8'
}
