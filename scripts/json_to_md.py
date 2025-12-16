import json

with open("report.json") as f:
	data = json.load(f)

lines = []
lines.append("| Feature | Scenario | Status | Time (s) |")
lines.append("|---------|---------|--------|----------|")

total_scenarios = 0
total_passed = 0
total_time = 0.0

for feature in data:
	feature_name = feature.get("name", "unknown feature")
	scenarios = feature.get("elements", [])
	for scenario in scenarios:
		scenario_name = scenario.get("name", "unknown scenario")
		steps = scenario.get("steps", [])
		passed = all(step["result"]["status"] == "passed" for step in steps)
		status = "✅ Passed" if passed else "❌ Failed"
		if passed:
			total_passed += 1
		total_scenarios += 1

		scenario_time = sum(step["result"].get("duration", 0) for step in steps)
		total_time += scenario_time

		lines.append(
			f"| {feature_name} | {scenario_name} | {status} | {scenario_time:.2f} |"
		)

lines.append(
	f"| **TOTAL** |  | {total_passed}/{total_scenarios} passed | {total_time:.2f} |"
)

with open("md_report.md", "w") as f:
	f.write("\n".join(lines))
