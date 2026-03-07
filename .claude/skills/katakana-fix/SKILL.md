# Katakana Compound Word Space Removal

Remove half-width spaces between katakana compound words in markdown files.

## Triggers

- `/katakana-fix`
- "katakana spacing"

## Instructions

Fix katakana compound word spacing in translation files. Katakana words should be concatenated without spaces (e.g., "スマートコントラクト" not "スマート コントラクト").

### Dry-run mode (preview changes)

To preview changes without modifying files:

```bash
perl -CSD -ne '
  if (/^```/) { $in_code = !$in_code }
  unless ($in_code) {
    $orig = $_;
    1 while s/([\x{30A0}-\x{30FF}]) ([\x{30A0}-\x{30FF}])/$1$2/g;
    print "$ARGV:$.: - $orig$ARGV:$.: + $_" if $orig ne $_;
  }
' <target_files>
```

### Execute mode (apply changes)

To apply the fix:

```bash
perl -CSD -i -pe '
  if (/^```/) { $in_code = !$in_code }
  unless ($in_code) {
    1 while s/([\x{30A0}-\x{30FF}]) ([\x{30A0}-\x{30FF}])/$1$2/g;
  }
' <target_files>
```

### Default targets

- `src/*.md` - all chapter files
- `glosary.md` - root glossary

### Verification

After applying, verify no katakana spaces remain (excluding code blocks):

```bash
perl -CSD -ne '
  if (/^```/) { $in_code = !$in_code }
  unless ($in_code) {
    print "$ARGV:$.: $_" if /([\x{30A0}-\x{30FF}]) ([\x{30A0}-\x{30FF}])/;
  }
' <target_files>
```

### Notes

- Handles multi-word compounds (A B C -> ABC) via repeated application
- Skips code blocks (``` delimited sections)
- Uses Unicode range \x{30A0}-\x{30FF} for katakana characters
