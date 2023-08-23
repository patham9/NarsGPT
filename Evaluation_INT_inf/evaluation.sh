move Correct.json CorrectBefore.json
move Incorrect.json IncorrectBefore.json
python3 1_GenerateTestOutput.py API_KEY=YOUR_KEY
python3 2_EvaluateTestOutput.py API_KEY=YOUR_KEY
python3 3_CheckDifferencesToLastRun.py > differences.txt
cat differences.txt
cat Scores.json
