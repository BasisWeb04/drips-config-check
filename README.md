# Campaign Config Check

This small command-line tool checks campaign JSON before launch. Its JSON format is a stand-in I designed from the job posting, not Drips' real configuration format.

A two-minute screen recording of the tool running is in [demo/demo.mp4](demo/demo.mp4).

It uses Python 3.11 or newer and the standard library only.

## Run it

```text
python -m campaign_check check examples/clean.json
python -m campaign_check check --all examples
python -m campaign_check rules
python -m unittest discover -s tests
```

Exit code 0 means the checked file or folder is clean. Exit code 1 means at least one error was found. Each message includes a rule ID, a JSON path, and a plain-language fix.

## Example JSON shape

The format has declared `data_fields` and `segments`, an `audience`, a dated `schedule` with a daily contact window, and a `flow` containing a start step plus linked SMS or call steps. See `examples/clean.json`.

## Checks and sources

| Rule | What it catches | Source |
| --- | --- | --- |
| CFG001 | Schedule start is not before schedule end | Drips posting: "configure customer campaigns ... and keep them running smoothly" and "Work with JSON-based configuration files" ([posting](https://www.linkedin.com/jobs/view/4475975483/)) |
| CFG002 | Contact window is outside 8 a.m. to 9 p.m. or not based on recipient local time | 47 CFR 64.1200(c)(1): telephone solicitation hours use local time at the called party's location ([public rule](https://www.law.cornell.edu/cfr/text/47/64.1200)) |
| CFG003 | An SMS lacks clear `Reply STOP` wording | 47 CFR 64.1200(a)(10): STOP and other listed reply words are recognized ways to revoke consent ([public rule](https://www.law.cornell.edu/cfr/text/47/64.1200)) |
| CFG004 | A message uses an undeclared merge field | Drips posting: campaign configuration and keeping campaigns running smoothly ([posting](https://www.linkedin.com/jobs/view/4475975483/)) |
| CFG005 | The flow start names no step | Drips posting: campaign configuration and keeping campaigns running smoothly ([posting](https://www.linkedin.com/jobs/view/4475975483/)) |
| CFG006 | A step cannot be reached from the flow start | Drips posting: campaign configuration and keeping campaigns running smoothly ([posting](https://www.linkedin.com/jobs/view/4475975483/)) |
| CFG007 | A `next` link names no step | Drips posting: campaign configuration and keeping campaigns running smoothly ([posting](https://www.linkedin.com/jobs/view/4475975483/)) |
| CFG008 | The audience names an undeclared segment | Drips posting: campaign configuration and keeping campaigns running smoothly ([posting](https://www.linkedin.com/jobs/view/4475975483/)) |
| CFG009 | Two flow steps use the same ID | Drips posting: campaign configuration and keeping campaigns running smoothly ([posting](https://www.linkedin.com/jobs/view/4475975483/)) |

CFG002 and CFG003 are conservative preflight checks, not a complete legal compliance review.
