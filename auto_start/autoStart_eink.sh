sleep 4
echo "$(ps -U root -f | grep "[I]nkB.py")" > /root/tmp2.txt
VARS="$(stat -c "%s" /root/tmp2.txt)"
sleep 1
printf '\nChecking InkB.py'
if [ "$VARS" -gt "1" ]
then
  printf '\nInkB.py Already Running\n\n'
else
  python3 /home/ink/InkB.py &
  printf '\nInkB.py Started\n\n'
fi
