# issue-DOC-TRIAGE-AMBIGUOUS-ADR-REF-01 — ADRからActive issueへの曖昧な参照を推測しない

- Type: Process / Documentation quality
- Status: Done
- Source Issue: N/A
- Priority: P1
- Scope: `01_Plans/triage_actionable_plans.py`, `01_Plans/tests/`
- Related ADR/Spec: `ADR-0000`
- Expected verification level: `unit`

## 背景

`triage_actionable_plans.py` は、Proposedなど作業対象のADRがどのActive issueに結び付いているかを表示するため、ADRの `Source Issue` をActive issueのpathへ解決しています。

移動前のpathが文書に残っている場合でも追跡できるよう、完全一致しない参照についてはbasenameを使った補完を行っていました。しかしActive issue側に同じbasenameのmemoが複数ある不正状態では、1対1の辞書へ変換した時点で候補が1件に潰れ、triage単体では最後に格納されたmemoを正しい参照先として扱う余地がありました。

通常の正本では既存のissue identity validatorが同一basenameの重複を拒否します。本対応はその検証を置き換えるものではなく、triageを単独で実行した場合にも誤った関係を作らないための第二の防御線です。

## 対応

ADRからActive issueへの参照解決を、次の順序に固定しました。

1. 正規化したpathがActive issueとして実在する場合は、その完全一致を採用する。
2. 完全一致しない場合だけbasenameによる補完を試みる。
3. basename候補が1件だけなら、移動後のmemoとして従来どおり解決する。
4. 候補が複数ある場合はどれも採用せず、候補pathを列挙したtriage errorを返す。

曖昧な参照が1件あっても、同じADRに別の一意なActive issue参照があれば、その確定できる関係までは保持します。

## 検証

回帰テストでは、次の3点を固定します。

- 同じbasenameのActive issueが複数ある場合、ADRをいずれかへ推測で結び付けないこと。
- 完全一致するpathがあれば、同名memoが別の場所に存在していても完全一致を優先すること。
- basename候補が1件だけなら、移動後memoへの補完を維持すること。

これにより、通常のrepository検証とtriage単体実行の双方で、参照先が不明な状態を「分かったこと」に変換しない境界を保ちます。
