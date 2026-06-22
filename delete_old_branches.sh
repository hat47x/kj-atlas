# === 3日以上経過したマージ済みブランチ削除コマンド ===
# 実行前に確認: git fetch origin --prune で最新化してください

# 1) codex/* ブランチ (2,442件)
git branch -r --merged origin/main | grep -E 'codex/|codex-' | sed 's|^[[:space:]]*origin/||' > /tmp/branches_to_delete.txt
echo "削除対象: $(wc -l < /tmp/branches_to_delete.txt) 件"

# 一括削除 (全件)
while read branch; do
  git push origin --delete "$branch"
done < /tmp/branches_to_delete.txt

# 2) 古い意味のあるブランチ (4件)
git push origin --delete \
  feat/domain-expr-01-readonly-state-surfacing \
  feat/domain-expr-01-state-filter \
  fix/ci-npm-econnreset-retry \
  plan/social-goal-domain-expression-phases

# 3) ローカル追跡ブランチの掃除
git remote prune origin
