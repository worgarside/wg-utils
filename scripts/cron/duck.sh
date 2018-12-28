#!/usr/bin/env bash
echo url="https://www.duckdns.org/update?domains=worgarside&token=439fa757-cde5-46be-93d9-204701c0bc14&ip=" | curl -k -o ~/Projects/wg-utils/logs/duck.log -K -