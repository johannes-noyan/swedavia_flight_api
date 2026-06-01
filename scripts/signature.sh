#!/bin/bash
echo "======================================================="
echo "Name:         Johannes Noyan"
echo "Email:        johannes_noyan@outlook.com"
echo "Timestamp:    $(date '+%Y-%m-%d %H:%M:%S')"
echo "Hostname:     $(hostname)"
echo "IP:           $(hostname -I | awk '{print $1}')"
echo "======================================================="
