# Chapter 5: Wallets
# 第5章：ウォレット

The word *wallet* is used to describe a few different things in Ethereum. At a high level, a wallet is a software application that serves as the primary user interface to Ethereum. The wallet controls access to a user's money, manages keys and addresses, tracks the balance, and creates and signs transactions. In addition, some Ethereum wallets can interact with contracts, such as ERC-20 tokens.

「ウォレット」という用語は、イーサリアムにおいていくつかの異なるものを表すために使われます。広義には、ウォレットとはイーサリアムへの主要なユーザーインターフェイスとして機能するソフトウェアアプリケーションのことです。ウォレットはユーザーの資金へのアクセスを制御し、鍵とアドレスの管理、残高の追跡、トランザクションの作成と署名を行います。さらに、一部のイーサリアムウォレットはERC-20トークンなどのコントラクトとやり取りすることもできます。

More narrowly, from a programmer's perspective, the word *wallet* refers to the system used to store and manage a user's keys. Every wallet has a key-management component. For some wallets, that's all there is. Other wallets are part of a much broader category, that of *browsers*, which are interfaces to Ethereum-based DApps, which we will examine in more detail in Chapter 12. There are no clear lines of distinction between the various categories that are conflated under the term *wallet*.

プログラマーの観点からより狭い意味で言えば、「ウォレット」という用語はユーザーの鍵を保管・管理するためのシステムを指します。すべてのウォレットには鍵管理コンポーネントがあります。一部のウォレットにとってはそれがすべてです。他のウォレットは*ブラウザ*というはるかに広いカテゴリーに属しています。ブラウザとはイーサリアムベースのDAppへのインターフェイスのことで、第12章で詳しく解説します。「ウォレット」という用語でまとめられているさまざまなカテゴリーの間には、明確な線引きはありません。

In this chapter, we will look at wallets as containers for private keys and as systems for managing these keys.

この章では、秘密鍵を保存するコンテナとして、また鍵を管理するシステムとして、ウォレットを解説します。

## Overview of Wallet Technologies
## ウォレット技術の概要

In this section, we summarize the various technologies used to construct user-friendly, secure, and flexible Ethereum wallets.

この節では、利便性、安全性、柔軟性を兼ね備えたイーサリアムウォレットを実現するために使われているさまざまな技術の概要を説明します。

One key consideration in designing wallets is balancing convenience and privacy. The most convenient Ethereum wallet is one with a single private key and address that you reuse for everything. Unfortunately, such a solution is a privacy nightmare since anyone can easily track and correlate all your transactions. Using a new key for every transaction is best for privacy but becomes very difficult to manage. The correct balance is difficult to achieve, which is why good wallet design is paramount.

ウォレット設計における重要な検討事項の1つは、利便性とプライバシーのバランスをとることです。最も使いやすいイーサリアムウォレットとは、すべてに対して1つの秘密鍵とアドレスを再利用するものでしょう。残念ながら、そのような設計ではプライバシーの観点から問題があります。なぜなら、誰もがあなたのトランザクションを簡単に追跡し、関連付けることができるからです。すべてのトランザクションに対して新しい鍵を使うことがプライバシーの観点からは最も望ましいのですが、管理は非常に難しくなります。適切なバランスをとることは困難な課題であり、だからこそ優れたウォレット設計が重要になります。

A common misconception about Ethereum is that Ethereum wallets contain ether or tokens. In fact, very strictly speaking, the wallet holds only keys. The ether or other tokens are recorded on the Ethereum blockchain. Users control the tokens on the network by signing transactions with the keys in their wallets. In a sense, an Ethereum wallet is a *keychain*. Having said that, given that the keys held by the wallet are the only things needed to transfer ether or tokens to others, in practice this distinction is fairly irrelevant.

イーサリアムに関するよくある誤解は、「イーサリアムのウォレットはイーサやトークンを保管している」というものです。実際には、非常に厳密に言えば、ウォレットは鍵しか保管していません。イーサや他のトークンはイーサリアムブロックチェーンに記録されています。ユーザーは自身のウォレットにある鍵でトランザクションに署名することで、ネットワーク上のトークンを制御します。ある意味、イーサリアムのウォレットは*キーチェーン*なのです。とはいえ、ウォレットに保管されている鍵は他人にイーサやトークンを転送するために必要な唯一のものであるため、実際にはこの区別はほとんど意味がありません。

Where the difference does matter is in changing one's mindset from dealing with the centralized system of conventional banking (where only you and the bank can see the money in your account, and you only need to convince the bank that you want to move funds to make a transaction) to the decentralized system of blockchain platforms (where everyone can see the ether balance of an account, although they probably don't know the account's owner, and everyone needs to be convinced that the owner wants to move funds for a transaction to be enacted). In practice, this means that there is an independent way to check an account's balance without needing its wallet. Moreover, you can move your account handling from your current wallet to a different wallet, if you grow to dislike the wallet app you started out using.

この違いが重要になるのは、従来の銀行の中央集権システム（あなたと銀行だけが口座の資金を確認でき、取引のために資金を移動するには銀行を説得するだけでよい）から、ブロックチェーンプラットフォームの分散型システム（誰もがアカウントのイーサ残高を見ることができるが、アカウントの所有者まではおそらくわからず、トランザクションを実行するには所有者が資金の移動を望んでいることを全員に納得させる必要がある）へと考え方を転換する場合です。実際にはこれは、ウォレットを必要とせずにアカウントの残高を確認する独立した方法があることを意味します。さらに、最初に使い始めたウォレットアプリが気に入らない場合は、現在のウォレットから別のウォレットにアカウント管理を移行することもできます。

> **Note**
>
> Ethereum wallets contain keys, not ether or tokens. Wallets are like keychains containing pairs of private and public keys. Users sign transactions with the private keys, thereby proving they own the ether. The ether is stored on the blockchain.

> **Note**
>
> イーサリアムのウォレットには、イーサやトークンではなく、鍵が保管されています。ウォレットは秘密鍵と公開鍵のペアを含むキーチェーンのようなものです。ユーザーは秘密鍵を使ってトランザクションに署名し、それによってイーサを所有していることを証明します。イーサはブロックチェーン上に保管されています。

There are two primary types of wallets, distinguished by whether the keys they contain are related to one another or not.

ウォレットには、主に2つの種類があります。両者の区別は、ウォレットが保持している鍵が互いに関連しているかどうかによります。

The first type is a *nondeterministic wallet*, where each key is independently generated from a different random number. The keys are not related to one another. This type of wallet is also known as a *JBOK wallet*, from the phrase "just a bunch of keys."

1つ目のタイプは*非決定性ウォレット*であり、それぞれの鍵は異なる乱数から独立に生成されます。鍵は互いに関連していません。このタイプのウォレットは「just a bunch of keys（鍵の束）」というフレーズから*JBOKウォレット*とも呼ばれています。

The second type of wallet is a *deterministic wallet*, where all the keys are derived from a single master key, known as the *seed*. All the keys in this type of wallet are related to one another and can be generated again if you have the original seed. Several different key-derivation methods are used in deterministic wallets. The most common derivation method uses a treelike structure, as described in "Hierarchical Deterministic Wallets (BIP-32/BIP-44)".

2つ目のタイプは*決定性ウォレット*です。すべての鍵は*シード*と呼ばれる1つのマスター鍵から導出されます。決定性ウォレット内のすべての鍵は互いに関連しており、元のシードがあれば再び生成することができます。決定性ウォレットではいくつかの異なる鍵導出方法が使用されています。最も一般的な導出方法は、「階層的決定性ウォレット（BIP-32/BIP-44）」で説明しているように、ツリー状の構造を用いたものです。

To make deterministic wallets slightly more secure against data-loss accidents, such as having your phone stolen or dropping it in the toilet, the seeds are often encoded as a list of words (in English or another language) for you to write down and use in case of an accident. These are known as the wallet's *mnemonic code words*. Of course, if someone gets hold of your mnemonic code words, then they can also re-create your wallet and thus gain access to your ether and smart contracts. As such, be very, very careful with your recovery word list! Never store it electronically, in a file on your computer or phone. Write it down on paper and store it in a safe, secure place.

携帯電話が盗まれたりトイレに落としたりするといったデータ消失事故に対して、決定性ウォレットの安全性を少しでも高める目的で、シードを単語のリスト（英語もしくは他の言語）にエンコードし、書き留めて、もしもの際に使えるようにすることがよくあります。これはウォレットの*ニーモニックコードワード*として知られています。もちろん、誰かがあなたのニーモニックコードワードを入手した場合、あなたのウォレットを再生成してイーサやスマートコントラクトにアクセスすることもできます。したがって、リカバリ用の単語リストの取り扱いには細心の注意を払ってください！電子的に保存してはいけません。コンピュータや携帯電話のファイルに保管してはいけません。紙に書き留め、安全で確実な場所に保管してください。

The next few sections introduce each of the wallet technologies at a high level.

次項以降では、それぞれのウォレット技術について概説します。

### Nondeterministic (Random) Wallets
### 非決定性（ランダム）ウォレット

In the first Ethereum wallet (produced for the Ethereum presale), each wallet file stored a single randomly generated private key. Such wallets are being replaced with deterministic wallets because these "old-style" wallets are in many ways inferior. For example, it is considered good practice to avoid reusing Ethereum addresses as part of maximizing your privacy while using Ethereum—that is, to use a new address (which needs a new private key) every time you receive funds. You can go further and use a new address for each transaction, although this can get expensive if you deal a lot with tokens. To follow this practice, a nondeterministic wallet will need to regularly increase its list of keys, which means you will need to make regular backups. If you ever lose your data (disk failure, drink accident, phone stolen) before you've managed to back up your wallet, you will lose access to your funds and smart contracts. The "type 0" nondeterministic wallets are the hardest to deal with because they create a new wallet file for every new address in a "just in time" manner.

最初のイーサリアムウォレット（イーサリアムのプレセールのために作られたもの）では、各ウォレットファイルにはランダムに生成された単一の秘密鍵が格納されていました。このような「古いスタイル」のウォレットは多くの点で劣っているため、決定性ウォレットで置き換えられつつあります。たとえば、イーサリアムを使用する際にプライバシーを最大限に保護するためには、イーサリアムアドレスの再利用を避けることが良い習慣とされています。つまり、資金を受け取るたびに新しいアドレス（新しい秘密鍵が必要）を使うことです。さらに踏み込んで、各トランザクションごとに新しいアドレスを使用することもできますが、トークンを大量に取り扱う場合にはコストが高くなります。この方法を採用すると、非決定性ウォレットは定期的に鍵のリストを増やす必要があり、定期的なバックアップが必要になります。ウォレットのバックアップを取る前にデータを失った場合（ディスクの故障、飲み物をこぼす、携帯電話の盗難）、資金やスマートコントラクトへのアクセスを失うことになります。「Type-0」の非決定性ウォレットは、新しいアドレスごとに「その場で」新しいウォレットファイルを作成するため、最も扱いにくい種類です。

Nevertheless, many Ethereum clients (including Geth) use a *keystore file*, which is a JSON-encoded file that contains a single (randomly generated) private key, encrypted by a passphrase for extra security. The JSON file's contents look like this:

それにもかかわらず、多くのイーサリアムクライアント（Gethを含む）は*キーストアファイル*を使用しています。これはJSONエンコードされたファイルで、ランダムに生成された秘密鍵が1つ含まれ、セキュリティを強化するためにパスフレーズで暗号化されています。JSONファイルの内容は次のようになります：

```json
{
    "address": "001d3f1ef827552ae1114027bd3ecf1f086ba0f9",
    "crypto": {
        "cipher": "aes-128-ctr",
        "ciphertext":
            "233a9f4d236ed0c13394b504b6da5df02587c8bf1ad8946f6f2b58f055507ece",
        "cipherparams": {
            "iv": "d10c6ec5bae81b6cb9144de81037fa15"
        },
        "kdf": "scrypt",
        "kdfparams": {
            "dklen": 32,
            "n": 262144,
            "p": 1,
            "r": 8,
            "salt":
                "99d37a47c7c9429c66976f643f386a61b78b97f3246adca89abe4245d2788407"
        },
        "mac": "594c8df1c8ee0ded8255a50caf07e8c12061fd859f4b7c76ab704b17c957e842"
    },
    "id": "4fcb2ba4-ccdb-424f-89d5-26cce304bf9c",
    "version": 3
}
```

The keystore format uses a *key derivation function* (KDF), also known as a *password-stretching algorithm*, which protects against brute-force, dictionary, and rainbow table attacks. In simple terms, the private key is not encrypted by the passphrase directly. Instead, the passphrase is "stretched" by repeatedly hashing it. The hashing function is repeated for 262,144 rounds, which can be seen in the keystore JSON as the parameter `crypto.kdfparams.n`. An attacker trying to brute-force the passphrase would have to apply 262,144 rounds of hashing for every attempted passphrase, which slows the attack sufficiently to make it infeasible for passphrases of appropriate complexity and length.

キーストア形式では*鍵導出関数*（KDF）を使用しています。これは*パスワードストレッチングアルゴリズム*とも呼ばれ、ブルートフォース（総当たり）攻撃、辞書攻撃、レインボーテーブル攻撃から保護します。簡単に言えば、秘密鍵はパスフレーズによって直接暗号化されるわけではありません。代わりに、パスフレーズに対して繰り返しハッシュ化を行う「ストレッチング」が行われます。ハッシュ関数は262,144ラウンド繰り返されます。この回数はキーストアJSONの`crypto.kdfparams.n`パラメータで確認できます。パスフレーズをブルートフォース攻撃しようとする攻撃者は、試行するパスフレーズごとに262,144ラウンドのハッシュ化を適用しなければならず、十分な複雑さと長さを持つパスフレーズに対する攻撃を実質的に不可能にします。

> **Tip**
>
> Using nondeterministic wallets is discouraged for anything other than simple tests. They are too cumbersome to back up and use for anything but the most basic of situations. Instead, use an industry standard–based hierarchical deterministic wallet with a mnemonic seed for backup.

> **Tip**
>
> 非決定性ウォレットの使用は、単純なテスト以外の用途では推奨されません。ごく基本的な状況以外では、バックアップして使うには扱いにくすぎます。代わりに、バックアップのためにニーモニックシードを用いる業界標準ベースの階層的決定性ウォレットを使用してください。

### Deterministic (Seeded) Wallets
### 決定性（シード）ウォレット

Deterministic or "seeded" wallets contain private keys that are all derived from a single master key, or seed. The seed is a randomly generated number that is combined with other data, such as an index number or "chain code" (see "Extended Public and Private Keys"), to derive any number of private keys. In a deterministic wallet, the seed is sufficient to recover all the derived keys, and therefore a single backup, at creation time, is sufficient to secure all the funds and smart contracts in the wallet. The seed is also sufficient for a wallet export or import, allowing for easy migration of all the keys between different wallet implementations.

決定性ウォレット、すなわち「シードウォレット」は、1つのマスター鍵もしくはシードから導出された秘密鍵を含むウォレットです。シードとはランダムに生成された数値で、インデックス番号や「チェーンコード」（「拡張公開鍵と拡張秘密鍵」を参照）などの他のデータと組み合わせて、任意の数の秘密鍵を導出します。決定性ウォレットでは、シードがあれば導出したすべての鍵を復元できるため、生成時にバックアップを1回取るだけで、ウォレット内のすべての資金とスマートコントラクトを保護できます。シードはウォレットのエクスポートやインポートにも十分であり、異なるウォレット実装間での鍵の移行を容易にします。

This design makes the security of the seed of utmost importance, as only the seed is needed to gain access to the entire wallet. On the other hand, being able to focus security efforts on a single piece of data can be seen as an advantage.

この設計では、シードのセキュリティが最も重要になります。シードだけあればウォレット全体へのアクセスを得ることができるからです。一方で、セキュリティ対策を1つのデータに集中できるという点は利点とも言えます。

### Hierarchical Deterministic Wallets (BIP-32/BIP-44)
### 階層的決定性ウォレット（BIP-32/BIP-44）

Deterministic wallets were developed to make it easy to derive many keys from a single seed. Currently, one of the most advanced forms of deterministic wallet is the *hierarchical deterministic (HD) wallet* defined by Bitcoin's BIP-32 standard. HD wallets contain keys derived in a tree structure, such that a parent key can derive a sequence of child keys, each of which can derive a sequence of grandchild keys, and so on. This tree structure is illustrated in Figure 5-1.

決定性ウォレットは、1つのシードから多くの鍵を容易に導出するために開発されました。現在、決定性ウォレットの最も進んだ形式の1つが、ビットコインのBIP-32標準で定義されている*階層的決定性（HD）ウォレット*です。HDウォレットには、ツリー構造で導出された鍵が含まれています。親鍵が一連の子鍵を導出し、それぞれの子鍵が一連の孫鍵を導出するというように続きます。このツリー構造を図5-1に示します。

![HD wallet: a tree of keys generated from a single seed](images/ch5/maet_0501.png)

Figure 5-1. HD wallet: a tree of keys generated from a single seed

図5-1. HDウォレット：1つのシードから生成された鍵ツリー

HD wallets offer a few key advantages over simpler deterministic wallets. First, the tree structure can be used to express additional organizational meaning, such as when a specific branch of subkeys is used to receive incoming payments and a different branch is used to receive change from outgoing payments. Branches of keys can also be used in corporate settings, where different branches can be allocated to departments, subsidiaries, specific functions, or accounting categories.

HDウォレットには、より単純な決定性ウォレットと比べていくつかの重要な利点があります。まず、ツリー構造を用いることで追加の用途を表現できます。たとえば、特定のサブキーのブランチを支払いの受け取りに使い、別のブランチを支払いのお釣りの受け取りに使うことができます。また、企業での利用として、異なるブランチを部門、子会社、特定の機能、会計カテゴリーに割り当てることもできます。

The second advantage of HD wallets is that users can create a sequence of public keys without having access to the corresponding private keys. This allows HD wallets to be used on an insecure server or in a watch-only or receive-only capacity, where the wallet doesn't have the private keys that can spend the funds.

HDウォレットのもう1つの利点は、対応する秘密鍵にアクセスすることなく公開鍵のシーケンスを生成できることです。これにより、安全でないサーバーや、閲覧専用もしくは受信専用の用途でHDウォレットを使うことができます。このようなウォレットは、資金を使うための秘密鍵を持ちません。

### Seeds and Mnemonic Codes (BIP-39)
### シードとニーモニックコード（BIP-39）

There are many ways to encode a private key for secure backup and retrieval. The currently preferred method is to use a sequence of words that, when taken together in the correct order, can uniquely re-create the private key. This is sometimes known as a *mnemonic*, and the approach has been standardized by BIP-39. Today, many Ethereum wallets (as well as wallets for other cryptocurrencies) use this standard and can import and export seeds for backup and recovery using interoperable mnemonics.

安全なバックアップと復元のために秘密鍵をエンコードする方法はたくさんあります。現在推奨されている方法は、正しい順序でまとめると秘密鍵を一意に再生成できる一連の単語を使用することです。これは*ニーモニック*と呼ばれることがあり、BIP-39で標準化されています。今日では、多くのイーサリアムウォレット（および他の暗号通貨ウォレット）がこの標準を使用しており、相互運用可能なニーモニックを用いてバックアップおよびリカバリ用のシードをインポート・エクスポートすることができます。

To see why this approach has become popular, let's have a look at an example:

このアプローチが普及した理由を理解するために、以下の例を見てみましょう：

```
FCCF1AB3329FD5DA3DA9577511F8F137 ← seed in hexadecimal
wolf juice proud gown wool unfair
wall cliff insect more detail hub ← seed using BIP-39 representation
```

In practical terms, the chance of an error when writing down the hex sequence is unacceptably high. In contrast, the list of known words is quite easy to deal with, mainly because there is a high level of redundancy in the writing of words (especially English words). If *inzect* had been recorded by accident, it could quickly be determined, upon the need for wallet recovery, that *inzect* is not a valid English word and that *insect* should be used instead. We are talking about writing down a representation of the seed because that is good practice when managing HD wallets: the seed is needed to recover the wallet in the case of data loss (whether through accident or theft), so keeping a backup is very prudent. However, the seed must be kept extremely private, so digital backups should be carefully avoided—hence, the advice to back up with pen and paper.

実際の問題として、16進数の文字列を書き留める際に転記ミスが発生する確率は容認できないほど高くなります。その一方で、既知の単語のリストは扱いがとても簡単です。主な理由は、単語（特に英語の単語）の書き取りには高い冗長性があるためです。もし誤って*inzect*が記録された場合、ウォレットのリカバリの際に*inzect*は正しい英単語ではなく、代わりに*insect*が使用されるべきだとすぐに判断できます。HDウォレットを管理する際にシードの表記を書き留めておくことを推奨しているのは、データの消失（事故や盗難）に備えてウォレットのリカバリにシードが必要になるためです。バックアップを取っておくことは非常に賢明です。ただし、シードは極めて秘密に保たなければならないため、デジタルバックアップは慎重に避けるべきです。ペンと紙でバックアップすることをおすすめします。

In summary, using a recovery word list to encode the seed for an HD wallet is the easiest way to safely export a private key set, transcribe it, record it on paper, read it without error, and import it into another wallet.

要約すると、HDウォレットのシードをエンコードしたリカバリワードリストを使用することが、秘密鍵のセットを安全にエクスポートし、転記し、紙に記録し、エラーなく読み取り、別のウォレットにインポートするための最も簡単な方法です。

## Wallet Best Practices
## ウォレットのベストプラクティス

As cryptocurrency wallet technology has matured, certain industry standards have emerged that make wallets broadly interoperable, easy to use, secure, and flexible. These standards also allow wallets to derive keys for multiple different cryptocurrencies, all from a single mnemonic. These standards are:

暗号通貨ウォレットの技術が成熟するにつれて、幅広い相互運用ができ、使いやすく安全で、柔軟性のあるウォレットを実現する業界標準が登場しました。これらの標準により、ウォレットは1つのニーモニックから複数の異なる暗号通貨の鍵を導出することもできます。それらの標準は以下の通りです：

- Mnemonic code words, based on BIP-39
- HD wallets, based on BIP-32
- A multipurpose HD wallet structure, based on BIP-43
- Multicurrency and multiaccount wallets, based on BIP-44

- BIP-39に基づくニーモニックコードワード
- BIP-32に基づくHDウォレット
- BIP-43に基づく多目的HDウォレット構造
- BIP-44に基づく多通貨・複数アカウントウォレット

These standards may change or be made obsolete by future developments, but for now, they form a set of interlocking technologies that have become the de facto wallet standard for most blockchain platforms and their cryptocurrencies.

これらの標準は将来の開発によって変わる可能性や時代遅れになる可能性もありますが、現時点ではそれぞれに連動した技術を形成しており、ほとんどのブロックチェーンプラットフォームとそれらの暗号通貨のデファクトスタンダードとなっています。

A broad range of software and hardware wallets have adopted the standards, making all these wallets interoperable. A user can export a mnemonic generated in one of these wallets and import it to another wallet, recovering all keys and addresses.

幅広いソフトウェアウォレットおよびハードウェアウォレットがこれらの標準を採用しており、すべて相互運用が可能です。ユーザーは、これらのウォレットの1つで生成されたニーモニックをエクスポートし、別のウォレットにインポートすることで、すべての鍵とアドレスをリカバリできます。

Some examples of software wallets supporting these standards include Rabby Wallet, MetaMask, and Phantom. Examples of hardware wallets supporting these standards are various models of Ledger and Trezor.

これらの標準をサポートするソフトウェアウォレットの例としては、Rabby Wallet、MetaMask、Phantomがあります。ハードウェアウォレットの例としては、LedgerおよびTrezorの各種モデルがあります。

The following sections examine each of these technologies in detail.

以下のセクションでは、これらの技術のそれぞれについて詳しく説明します。

> **Tip**
>
> If you are implementing an Ethereum wallet, it should be built as an HD wallet, with a seed encoded as a mnemonic code for backup, following the BIP-32, BIP-39, BIP-43, and BIP-44 standards, as described in the following sections.

> **Tip**
>
> イーサリアムウォレットを実装する場合は、以下のセクションで説明するBIP-32、BIP-39、BIP-43、BIP-44の標準に従い、バックアップ用のニーモニックコードとしてエンコードされたシードを持つHDウォレットとして構築する必要があります。

### Mnemonic Code Words (BIP-39)
### ニーモニックコードワード（BIP-39）

Mnemonic code words are word sequences that encode a random number used as a seed to derive a deterministic wallet. The sequence of words is sufficient to re-create the seed and, from there, to re-create the wallet and all the derived keys. A wallet application that implements deterministic wallets with mnemonic words will show the user a sequence of 12–24 words when first creating a wallet. That sequence of words is the wallet backup and can be used to recover and re-create all the keys in the same or any compatible wallet application. As we explained earlier, mnemonic word lists make it easier for users to back up wallets because they are easy to read and correctly transcribe.

ニーモニックコードワードとは、決定性ウォレットを導出するためのシードとして使用される乱数をエンコードした単語のシーケンスです。この単語のシーケンスがあればシードを再生成でき、そこからウォレットとすべての導出鍵を再生成できます。ニーモニックワードを用いた決定性ウォレットを実装するウォレットアプリケーションは、ウォレットの初回作成時にユーザーに12〜24個の単語のシーケンスを表示します。この単語のシーケンスがウォレットのバックアップであり、同じまたは互換性のあるウォレットアプリケーションですべての鍵を復元・再生成するために使用できます。先に説明したように、ニーモニックワードのリストは可読性が高く正確に転記できるため、ユーザーはウォレットを簡単にバックアップできます。

> **Note**
>
> Mnemonic words are often confused with *brainwallets*. They are not the same. The primary difference is that a brainwallet consists of words chosen by the user, whereas mnemonic words are created randomly by the wallet and presented to the user. This important difference makes mnemonic words much more secure because humans are very poor sources of randomness. Perhaps more important, using the term *brainwallet* suggests that the words have to be memorized, which is a terrible idea and a recipe for not having your backup when you need it.

> **Note**
>
> ニーモニックワードはよく*ブレインウォレット*と混同されますが、両者は同じものではありません。主な違いは、ブレインウォレットはユーザーが選択した単語で構成されるのに対し、ニーモニックワードはウォレットによってランダムに生成されてユーザーに提示されることです。この重要な違いにより、ニーモニックワードははるかに安全なものになっています。なぜなら、人間はランダム性の生成源としてとても乏しいからです。おそらくもっと重要なのは、*ブレインウォレット*という用語が単語を暗記しなければならないことを示唆している点です。これはひどいアイデアであり、必要なときにバックアップが手元にないという事態を招きます。

Mnemonic codes are defined in BIP-39. Note that BIP-39 is one implementation of a mnemonic code standard. There is a different standard, with a different set of words, used by the Electrum Bitcoin wallet and predating BIP-39. BIP-39 was proposed by the company behind the Trezor hardware wallet and is incompatible with Electrum's implementation. However, BIP-39 has now achieved broad industry support across dozens of interoperable implementations and should be considered the de facto industry standard. Furthermore, BIP-39 can be used to produce multicurrency wallets supporting Ethereum, whereas Electrum seeds cannot.

ニーモニックコードはBIP-39で定義されています。ただし、BIP-39はニーモニックコード標準の1つの実装にすぎないことに注意してください。ビットコインウォレットのElectrumは、BIP-39に先行して、異なる単語セットを持つ別の標準を使用しています。BIP-39はTrezorハードウェアウォレットを製造する企業によって提案されたもので、Electrumの実装とは互換性がありません。しかし、BIP-39は現在、数十の相互運用可能な実装にわたって幅広い業界サポートを得ており、デファクトスタンダードと見なされています。さらに、BIP-39はイーサリアムをサポートする多通貨ウォレットの作成に使用できますが、Electrumのシードはそれができません。

BIP-39 defines the creation of a mnemonic code and seed, which we describe here in nine steps. For clarity, the process is split into two parts: steps 1 through 6 are listed in "Generating mnemonic words", and steps 7 through 9 are listed in "From mnemonic to seed".

BIP-39はニーモニックコードとシードの生成手順を定義しています。ここでは9つのステップで説明します。理解しやすくするために、プロセスを2つの部分に分けています。ステップ1〜6は「ニーモニックワードの生成」に、ステップ7〜9は「ニーモニックからシードへ」に記載しています。

#### Generating mnemonic words
#### ニーモニックワードの生成

The wallet generates mnemonic words automatically using the standardized process defined in BIP-39. The wallet starts from a source of entropy, adds a checksum, and then maps the entropy to a word list following these steps:

ウォレットはBIP-39で定義された標準化されたプロセスを使用して、ニーモニックワードを自動的に生成します。ウォレットはエントロピー源から開始し、チェックサムを追加した後、以下のステップに従ってエントロピーを単語リストにマッピングします：

1. Create a cryptographically random sequence *S* of 128–256 bits.

1. 128〜256ビットの暗号論的にランダムなシーケンス*S*を生成する。

2. Create a checksum of *S* by taking the first length-of-*S* ÷ 32 bits of the SHA-256 hash of *S*.

2. *S*のSHA-256ハッシュの先頭（*S*のビット長÷32）ビットを取り、*S*のチェックサムを生成する。

3. Add the checksum to the end of the random sequence *S*.

3. チェックサムをランダムなシーケンス*S*の末尾に追加する。

4. Divide the sequence-and-checksum concatenation into sections of 11 bits.

4. シーケンスとチェックサムの連結を11ビットずつのセクションに分割する。

5. Map each 11-bit value to a word from the predefined dictionary of 2,048 words.

5. 各11ビットの値を、あらかじめ定義された2,048語の辞書の中の単語にマッピングする。

6. Create the mnemonic code from the sequence of words, maintaining the order.

6. 順序を維持しながら、一連の単語からニーモニックコードを生成する。

Figure 5-2 shows how entropy is used to generate mnemonic words.

図5-2は、エントロピーを使用してニーモニックワードを生成する方法を示しています。

![Generating mnemonic words](images/ch5/maet_0502.png)

Figure 5-2. Generating mnemonic words

図5-2. ニーモニックワードの生成

Table 5-1 shows the relationship between the size of the entropy data and the length of mnemonic codes in words.

表5-1は、エントロピーデータのサイズとニーモニックコードの単語数の関係を示しています。

**Table 5-1. Mnemonic codes: Entropy and word length**

**表5-1. ニーモニックコード：エントロピーと単語数**

| Entropy (bits) | Checksum (bits) | Entropy + checksum (bits) | Mnemonic length (words) |
|---|---|---|---|
| 128 | 4 | 132 | 12 |
| 160 | 5 | 165 | 15 |
| 192 | 6 | 198 | 18 |
| 224 | 7 | 231 | 21 |
| 256 | 8 | 264 | 24 |

#### From mnemonic to seed
#### ニーモニックからシードへ

The mnemonic words represent entropy with a length of 128–256 bits. The entropy is then used to derive a longer (512-bit) seed through the use of the key-stretching function PBKDF2. The seed produced is used to build a deterministic wallet and derive its keys.

ニーモニックワードは128〜256ビットの長さを持つエントロピーを表しています。このエントロピーは、鍵ストレッチ関数PBKDF2を用いてより長い（512ビット）シードを導出するために使われます。生成されたシードは、決定性ウォレットを構築し、その鍵を導出するために使われます。

The key-stretching function takes two parameters: the mnemonic and a salt. The purpose of a salt in a key-stretching function is to make it difficult to build a lookup table enabling a brute-force attack. In the BIP-39 standard, the salt has another purpose: it allows for the introduction of a passphrase that serves as an additional security factor protecting the seed, which we will describe in more detail in the next section.

鍵ストレッチ関数には2つのパラメータがあります：ニーモニックとソルトです。鍵ストレッチ関数におけるソルトの目的は、ブルートフォース攻撃を可能にするルックアップテーブルの構築を困難にすることです。BIP-39標準では、ソルトにはもう1つの目的があります。それは、シードを保護する追加のセキュリティ要素として機能するパスフレーズの導入を可能にすることで、次のセクションで詳しく説明します。

The process continues from the previous section with the following steps:

プロセスは前のセクションから続き、以下のステップで進みます：

7. The first parameter to the PBKDF2 key-stretching function is the mnemonic produced in step 6.

7. PBKDF2鍵ストレッチ関数の最初のパラメータは、ステップ6で生成されたニーモニックである。

8. The second parameter to the PBKDF2 key-stretching function is a *salt*. The salt is composed of the string constant `"mnemonic"` concatenated with an optional user-supplied passphrase.

8. PBKDF2鍵ストレッチ関数の2番目のパラメータは*ソルト*である。ソルトは、文字列定数`"mnemonic"`にユーザーが任意で提供するパスフレーズ文字列を連結して構成される。

9. PBKDF2 stretches the mnemonic and salt parameters using 2,048 rounds of hashing with the HMAC-SHA512 algorithm, producing a 512-bit value as its final output. That 512-bit value is the seed.

9. PBKDF2は、HMAC-SHA512アルゴリズムによる2,048ラウンドのハッシュ化を使用してニーモニックとソルトのパラメータをストレッチし、最終出力として512ビットの値を生成する。この512ビットの値がシードである。

Figure 5-3 shows how a mnemonic is used to generate a seed.

図5-3は、ニーモニックを使用してシードを生成する方法を示しています。

![From mnemonic to seed](images/ch5/maet_0503.png)

Figure 5-3. From mnemonic to seed

図5-3. ニーモニックからシードへ

> **Note**
>
> The key-stretching function, with its 2,048 rounds of hashing, is a somewhat effective protection against brute-force attacks against the mnemonic or the passphrase. It makes it costly (in computation) to try more than a few thousand passphrase and mnemonic combinations, while the number of possible derived seeds is vast (2^512^, or about 10^154^)—far bigger than the number of atoms in the visible universe (about 10^80^).

> **Note**
>
> 2,048ラウンドのハッシュ化を行う鍵ストレッチ関数は、ニーモニックやパスフレーズに対するブルートフォース攻撃に対していくらか効果的な保護手段です。数千ものパスフレーズとニーモニックの組み合わせを試すにはかなりの計算コストがかかります。一方で、取り得るシードの数は膨大です（2^512^、すなわち約10^154^）。これは可視宇宙に存在する原子の数（約10^80^）よりもはるかに多いのです。

Tables 5-2, 5-3, and 5-4 show some examples of mnemonic codes and the seeds they produce.

表5-2、5-3、5-4にニーモニックコードとそれらが生成するシードの例を示します。

**Table 5-2. A 128-bit entropy mnemonic code with no passphrase and the resulting seed**

**表5-2. 128ビットエントロピーのニーモニックコード（パスフレーズなし）と生成されるシード**

| | |
|---|---|
| **Entropy** | 0c1e24e5917779d297e14d45f14e1a1a |
| **Mnemonic** | army van defense carry jealous true garbage claim echo media make crunch |
| **Passphrase** | (none) |
| **Seed** | 5b56c417303faa3fcba7e57400e120a0ca83ec5a4fc9ffba757fbe63fbd77a89a1a3be4c67196f57c39... |

**Table 5-3. A 128-bit entropy mnemonic code with a passphrase and the resulting seed**

**表5-3. 128ビットエントロピーのニーモニックコード（パスフレーズあり）と生成されるシード**

| | |
|---|---|
| **Entropy** | 0c1e24e5917779d297e14d45f14e1a1a |
| **Mnemonic** | army van defense carry jealous true garbage claim echo media make crunch |
| **Passphrase** | SuperDuperSecret |
| **Seed** | 3b5df16df2157104cfdd22830162a5e170c0161653e3afe6c88defeefb0818c793dbb28ab3ab091897d0... |

**Table 5-4. A 256-bit entropy mnemonic code with no passphrase and the resulting seed**

**表5-4. 256ビットエントロピーのニーモニックコード（パスフレーズなし）と生成されるシード**

| | |
|---|---|
| **Entropy** | 2041546864449caff939d32d574753fe684d3c947c3346713dd8423e74abcf8c |
| **Mnemonic** | cake apple borrow silk endorse fitness top denial coil riot stay wolf luggage oxygen faint major edit measure invite love trap field dilemma oblige |
| **Passphrase** | (none) |
| **Seed** | 3269bce2674acbd188d4f120072b13b088a0ecf87c6e4cae41657a0bb78f5315b33b3a04356e53d062e5... |

#### Optional Passphrase in BIP-39
#### BIP-39のオプションのパスフレーズ

The BIP-39 standard allows for the use of an optional passphrase in the derivation of the seed. If no passphrase is used, the mnemonic is stretched with a salt consisting of the constant string `"mnemonic"`, producing a specific 512-bit seed from any given mnemonic. If a passphrase is used, the stretching function produces a *different* seed from that same mnemonic. In fact, given a single mnemonic, every possible passphrase leads to a different seed. Essentially, there is no "wrong" passphrase. All passphrases are valid, and they all lead to different seeds, forming a vast set of possible uninitialized wallets. The set of possible wallets is so large (2^512^) that there is no practical possibility of brute-forcing or accidentally guessing one that is in use, as long as the passphrase has sufficient complexity and length.

BIP-39標準では、シードの導出にオプションのパスフレーズを使用できます。パスフレーズが使用されない場合、ニーモニックは定数文字列`"mnemonic"`からなるソルトでストレッチされ、任意のニーモニックから特定の512ビットのシードが生成されます。パスフレーズが使用される場合、ストレッチ関数は同じニーモニックから*異なる*シードを生成します。実際には、1つのニーモニックに対して、あらゆるパスフレーズが異なるシードを生成します。基本的に「間違った」パスフレーズは存在しません。すべてのパスフレーズは有効であり、すべてが異なるシードを生成し、膨大な数の初期化されていないウォレットを形成します。生成可能なウォレットの数は非常に大きく（2^512^）、パスフレーズの複雑さと長さが十分である限り、使用中のものをブルートフォース攻撃で発見したり偶然推測したりする実用的な可能性はありません。

> **Tip**
>
> There are no "wrong" passphrases in BIP-39. Every passphrase leads to some wallet, which unless previously used will be empty.

> **Tip**
>
> BIP-39には「間違った」パスフレーズは存在しません。あらゆるパスフレーズは何らかのウォレットを生成します。そのウォレットは、以前に使用されていない限り空です。

The optional passphrase creates two important features:

オプションのパスフレーズは2つの重要な機能を提供します：

- A second factor (something memorized) that makes a mnemonic useless on its own, protecting mnemonic backups from compromise by a thief

- 第2の要素（暗記したもの）により、ニーモニック単独では使えないようにし、泥棒による漏洩からニーモニックのバックアップを保護する

- A form of plausible deniability or "duress wallet," where a chosen passphrase leads to a wallet with a small amount of funds, used to distract an attacker from the "real" wallet that contains the majority of funds

- もっともらしい否認可能性、すなわち「脅迫ウォレット」の形態。選択されたパスフレーズにより少額の資金が入ったウォレットが生成され、大半の資金が入っている「本物」のウォレットから攻撃者の注意をそらすために使用される

However, it is important to note that the use of a passphrase also introduces the risk of loss:

ただし、パスフレーズの使用は紛失のリスクも伴うことに注意が必要です：

- If the wallet owner is incapacitated or dead and no one else knows the passphrase, the seed is useless, and all the funds stored in the wallet are lost forever.

- ウォレットの所有者が行動不能になったり死亡し、誰もパスフレーズを知らない場合、シードは役に立たず、ウォレットに保管されているすべての資金は永久に失われる。

- Conversely, if the owner backs up the passphrase in the same place as the seed, that defeats the purpose of a second factor.

- 逆に、所有者がシードと同じ場所にパスフレーズをバックアップすると、第2の要素としての目的を果たさなくなる。

While passphrases are very useful, they should be used only in combination with a carefully planned process for backup and recovery, considering the possibility of heirs surviving the owner being able to recover the cryptocurrency.

パスフレーズは非常に便利ですが、相続人が所有者の死後に暗号通貨をリカバリできるようにすることも考慮した、バックアップとリカバリのための慎重に計画されたプロセスと組み合わせてのみ使用すべきです。

#### Working with Mnemonic Codes
#### ニーモニックコードとの連携

BIP-39 is implemented as a library in many different programming languages, such as:

BIP-39は多くのプログラミング言語でライブラリとして実装されています。

**python-mnemonic**

The reference implementation of the standard by the SatoshiLabs team that proposed BIP-39, in Python

BIP-39を提案したSatoshiLabsチームによるリファレンス実装（Python）

**ConsenSys/eth-lightwallet**

A lightweight JavaScript Ethereum wallet for nodes and browser (with BIP-39)

ノードとブラウザ向けの軽量JavaScriptイーサリアムウォレット（BIP-39対応）

**npm/bip39**

A JavaScript implementation of Bitcoin BIP-39

ビットコインBIP-39のJavaScript実装

There is also a BIP-39 generator implemented in a standalone web page (Figure 5-4), which is extremely useful for testing and experimentation. The [Mnemonic Code Converter](https://iancoleman.io/bip39/) generates mnemonics, seeds, and extended private keys. It can be used offline in a browser, or it can be accessed online.

スタンドアロンのウェブページとして実装されたBIP-39ジェネレーターもあり（図5-4）、テストや実験に非常に便利です。[Mnemonic Code Converter](https://iancoleman.io/bip39/)はニーモニック、シード、拡張秘密鍵を生成します。ブラウザでオフラインで使用することも、オンラインでアクセスすることもできます。

> **Note**
>
> This will be emphasized repeatedly throughout the chapter because it is the most crucial rule for seed security: never, under any circumstances, save your seed phrase in digital form.

> **注記**
>
> この章を通じて繰り返し強調されますが、シードのセキュリティにおいて最も重要なルールです：いかなる状況においても、シードフレーズをデジタル形式で保存してはいけません。

![The BIP-39 generator web page](images/ch5/maet_0504.png)

Figure 5-4. The BIP-39 generator web page

図5-4. BIP-39ジェネレーターのウェブページ

### Creating an HD Wallet from the Seed
### シードからのHDウォレットの作成

HD wallets are created from a single *root seed*, which is a 128-, 256-, or 512-bit random number. This seed is most commonly generated from a mnemonic, as detailed in the previous section.

HDウォレットは、128ビット、256ビット、または512ビットの乱数である単一の*ルートシード*から生成されます。このシードは、前節で説明したように、最も一般的にはニーモニックから生成されます。

Every key in the HD wallet is deterministically derived from this root seed, which makes it possible to re-create the entire HD wallet from that seed in any compatible HD wallet. This makes it easy to export, back up, restore, and import HD wallets containing thousands or even millions of keys by transferring just the mnemonic from which the root seed is derived.

HDウォレット内のすべての鍵はこのルートシードから決定論的に導出されるため、互換性のあるHDウォレットであれば、そのシードからHDウォレット全体を再作成することが可能です。これにより、ルートシードの導出元であるニーモニックを転送するだけで、数千、場合によっては数百万の鍵を含むHDウォレットのエクスポート、バックアップ、復元、インポートが容易になります。

### HD Wallets (BIP-32)
### HDウォレット（BIP-32）

Most HD wallets follow the BIP-32 standard, which has become a de facto industry standard for deterministic key generation. We won't be discussing all the details of BIP-32 here, only the components necessary to understand how it is used in wallets. The most important aspect is the treelike hierarchical relationships that it is possible for the derived keys to have, as you can see in Figure 5-1. It's also important to understand the ideas of extended keys and hardened keys, which are explained in the following sections.

ほとんどのHDウォレットはBIP-32標準に準拠しており、決定論的な鍵生成のデファクトスタンダードとなっています。ここではBIP-32のすべての詳細を議論するのではなく、ウォレットでの使われ方を理解するために必要なコンポーネントのみを説明します。最も重要な点は、図5-1で見られるように、導出された鍵がツリー状の階層的な関係を持てることです。拡張鍵と強化鍵の概念を理解することも重要であり、これらは以降の節で説明します。

There are dozens of interoperable implementations of BIP-32 offered in many software libraries. These are mostly designed for Bitcoin wallets, which implement addresses in a different way, but they share the same key-derivation implementation as Ethereum's BIP-32-compatible wallets. Use one designed for Ethereum or adapt one from Bitcoin by adding an Ethereum address encoding library.

多くのソフトウェアライブラリで、相互運用可能なBIP-32の実装が数多く提供されています。これらの多くはビットコインウォレット向けに設計されており、アドレスの実装方法は異なりますが、イーサリアムのBIP-32互換ウォレットと同じ鍵導出の実装を共有しています。イーサリアム向けに設計されたものを使用するか、ビットコイン向けのものにイーサリアムアドレスのエンコーディングライブラリを追加して適用してください。

There is also a BIP-32 generator implemented as a standalone web page that is very useful for testing and experimentation with BIP-32.

スタンドアロンのウェブページとして実装されたBIP-32ジェネレーターもあり、BIP-32のテストや実験に非常に便利です。

> **Warning**
>
> The standalone BIP-32 generator is not an HTTPS site. That's to remind you that using this tool is not secure. It is only for testing. You should not use the keys produced by this site with real funds.

> **警告**
>
> スタンドアロンのBIP-32ジェネレーターはHTTPSサイトではありません。これはこのツールの使用が安全でないことを示しています。テスト専用です。このサイトで生成された鍵を実際の資金に使用してはいけません。

#### Extended Public and Private Keys
#### 拡張公開鍵と拡張秘密鍵

In BIP-32 terminology, keys can be "extended." With the right mathematical operations, these extended "parent" keys can be used to derive "child" keys, thus producing the hierarchy of keys and addresses described earlier. A parent key doesn't have to be at the top of the tree. It can be picked out from anywhere in the tree hierarchy. Extending a key involves taking the key itself and appending a special *chain code* to it. A chain code is a 256-bit binary string that is mixed with each key to produce child keys.

BIP-32の用語では、鍵は「拡張」することができます。適切な数学的演算を用いることで、これらの拡張された「親」鍵から「子」鍵を導出し、前述した鍵とアドレスの階層構造を生成できます。親鍵はツリーの最上位にある必要はなく、ツリー階層のどこからでも選択できます。鍵を拡張するとは、鍵自体に特別な*チェーンコード*を付加することです。チェーンコードは256ビットのバイナリ文字列で、各鍵と混合されて子鍵を生成します。

If the key is a private key, it becomes an *extended private key* distinguished by the prefix `xprv`:

鍵が秘密鍵である場合、プレフィックス`xprv`で識別される*拡張秘密鍵*になります：

    xprv9s21ZrQH143K2JF8RafpqtKiTbsbaxEeUaMnNHsm5o6wCW3z8ySyH4UxFVSfZ8n7ESu7fgir8i...

An *extended public key* is distinguished by the prefix `xpub`:

*拡張公開鍵*はプレフィックス`xpub`で識別されます：

    xpub661MyMwAqRbcEnKbXcCqD2GT1di5zQxVqoHPAgHNe8dv5JP8gWmDproS6kFHJnLZd23tWevhdn...

A very useful characteristic of HD wallets is the ability to derive child public keys from parent public keys *without* having the private keys. This gives us two ways to derive a child public key: either directly from the child private key or from the parent public key. An extended public key can be used, therefore, to derive all the public keys (and *only* the public keys) in that branch of the HD wallet structure.

HDウォレットの非常に便利な特性は、秘密鍵を*持たずに*親公開鍵から子公開鍵を導出できることです。これにより、子公開鍵を導出する方法が2つあります：子秘密鍵から直接導出する方法と、親公開鍵から導出する方法です。したがって、拡張公開鍵を使用して、HDウォレット構造のそのブランチ内のすべての公開鍵（公開鍵*のみ*）を導出できます。

This shortcut can be used to create extremely secure public-key-only deployments, where a server or application has a copy of an extended public key but no private keys whatsoever. That kind of deployment can produce an infinite number of public keys and Ethereum addresses but cannot spend any money sent to those addresses. Meanwhile, on another, more secure server, the extended private key can derive all the corresponding private keys to sign transactions and spend the money.

このショートカットを利用することで、サーバーやアプリケーションが拡張公開鍵のコピーを持ちながら秘密鍵を一切持たない、きわめて安全な公開鍵のみのデプロイメントを構築できます。この種のデプロイメントは、無限の公開鍵とイーサリアムアドレスを生成できますが、それらのアドレスに送られた資金を使うことはできません。一方、別のより安全なサーバーで、拡張秘密鍵から対応するすべての秘密鍵を導出して、トランザクションに署名し資金を使うことができます。

One common application of this method is to install an extended public key on a web server that serves an ecommerce application. The web server can use the public key derivation function to create a new Ethereum address for every transaction (e.g., for a customer shopping cart) and will not have any private keys that would be vulnerable to theft. Without HD wallets, the only way to do this is to generate thousands of Ethereum addresses on a separate secure server and then preload them on the ecommerce server. That approach is cumbersome and requires constant maintenance to ensure that the server doesn't run out of keys—hence the preference to use extended public keys from HD wallets.

この方法の一般的な用途の1つは、eコマースアプリケーションを提供するウェブサーバーに拡張公開鍵をインストールすることです。ウェブサーバーは公開鍵導出関数を使用して、トランザクションごと（例えば、顧客のショッピングカートごと）に新しいイーサリアムアドレスを作成でき、盗難に対して脆弱な秘密鍵を一切持ちません。HDウォレットがなければ、これを実現する唯一の方法は、別の安全なサーバーで数千のイーサリアムアドレスを生成し、eコマースサーバーに事前にロードすることです。このアプローチは煩雑であり、サーバーの鍵が枯渇しないように常にメンテナンスが必要です。そのため、HDウォレットの拡張公開鍵を使用する方が好まれます。

Another common application of this solution is for cold-storage or hardware wallets. In that scenario, the extended private key can be stored in a hardware wallet, while the extended public key can be kept online. The user can create "receive" addresses at will while the private keys are safely stored offline. To spend the funds, the user can use the extended private key in an offline signing Ethereum client or sign transactions on the hardware wallet device.

この方法のもう1つの一般的な用途は、コールドストレージやハードウェアウォレットです。このシナリオでは、拡張秘密鍵をハードウェアウォレットに保管し、拡張公開鍵はオンラインで保持できます。ユーザーは秘密鍵が安全にオフラインで保管されたまま、自由に「受信」アドレスを作成できます。資金を使うには、オフライン署名のイーサリアムクライアントで拡張秘密鍵を使用するか、ハードウェアウォレットデバイスでトランザクションに署名します。

#### Hardened Child Key Derivation
#### 強化子鍵導出

The ability to derive a branch of public keys from an extended public key, or `xpub`, is very useful, but it comes with potential risk. Access to an `xpub` does not give access to child private keys. However, because the `xpub` contains the chain code (used to derive child public keys from the parent public key), if a child private key is known or somehow leaked, it can be used with the chain code to derive all the other child private keys. A single leaked child private key, together with a parent chain code, reveals all the private keys of all the children. Worse, the child private key together with a parent chain code can be used to deduce the parent private key.

拡張公開鍵（`xpub`）から公開鍵のブランチを導出する機能は非常に便利ですが、潜在的なリスクを伴います。`xpub`へのアクセスは子秘密鍵へのアクセスを与えません。しかし、`xpub`にはチェーンコード（親公開鍵から子公開鍵を導出するために使用される）が含まれているため、子秘密鍵が判明したり何らかの形で漏洩した場合、チェーンコードと組み合わせて他のすべての子秘密鍵を導出できてしまいます。1つの子秘密鍵の漏洩と親チェーンコードにより、すべての子のすべての秘密鍵が明らかになります。さらに悪いことに、子秘密鍵と親チェーンコードを使って親秘密鍵を推定することも可能です。

To counter this risk, HD wallets use an alternative derivation function called *hardened derivation*, which "breaks" the relationship between parent public key and child chain code. The hardened derivation function uses the parent private key to derive the child chain code, instead of the parent public key. This creates a "firewall" in the parent-child sequence, with a chain code that cannot be used to compromise a parent or sibling private key.

このリスクに対抗するため、HDウォレットは*強化導出*と呼ばれる代替の導出関数を使用します。これは親公開鍵と子チェーンコードの間の関係を「断ち切る」ものです。強化導出関数は、親公開鍵の代わりに親秘密鍵を使用して子チェーンコードを導出します。これにより、親子間のシーケンスに「ファイアウォール」が作成され、親や兄弟の秘密鍵を危殆化させるために使用できないチェーンコードが生成されます。

In simple terms, if you want to use the convenience of an `xpub` to derive branches of public keys without exposing yourself to the risk of a leaked chain code, you should derive it from a hardened parent, rather than a normal parent. Best practice is to have the level-one children of the master keys always derived by hardened derivation, to prevent compromise of the master keys.

簡単に言えば、チェーンコード漏洩のリスクにさらされることなく`xpub`の便利さを利用して公開鍵のブランチを導出したい場合は、通常の親ではなく、強化された親から導出すべきです。ベストプラクティスは、マスター鍵の危殆化を防ぐために、マスター鍵の第1レベルの子は常に強化導出で導出することです。

#### Index Numbers for Normal and Hardened Derivation
#### 通常導出と強化導出のインデックス番号

It is clearly desirable to be able to derive more than one child key from a given parent key. To manage this, an index number is used. Each index number, when combined with a parent key using the special child derivation function, gives a different child key. The index number used in the BIP-32 parent-to-child derivation function is a 32-bit integer. To easily distinguish between keys derived through the normal (unhardened) derivation function versus keys derived through hardened derivation, this index number is split into two ranges. Index numbers between 0 and 2^31^–1 (0x0 to 0x7FFFFFFF) are used *only* for normal derivation. Index numbers between 2^31^ and 2^32^–1 (0x80000000 to 0xFFFFFFFF) are used *only* for hardened derivation. Therefore, if the index number is less than 2^31^, the child is normal, whereas if the index number is equal to or above 2^31^, the child is hardened.

与えられた親鍵から複数の子鍵を導出できることは明らかに望ましいことです。これを管理するために、インデックス番号が使用されます。各インデックス番号は、特別な子導出関数を使って親鍵と組み合わされると、異なる子鍵を生成します。BIP-32の親から子への導出関数で使用されるインデックス番号は32ビット整数です。通常（非強化）導出関数で導出された鍵と強化導出で導出された鍵を容易に区別するために、このインデックス番号は2つの範囲に分割されています。0から2^31^-1（0x0から0x7FFFFFFF）のインデックス番号は通常導出*のみ*に使用されます。2^31^から2^32^-1（0x80000000から0xFFFFFFFF）のインデックス番号は強化導出*のみ*に使用されます。したがって、インデックス番号が2^31^未満であれば子は通常、2^31^以上であれば子は強化です。

To make the index numbers easier to read and display, the index numbers for hardened children are displayed starting from zero, but with a prime symbol. The first normal child key is therefore displayed as 0, whereas the first hardened child (index 0x80000000) is displayed as 0′. In sequence, then, the second hardened key would have an index of 0x80000001 and would be displayed as 1′, and so on. When you see an HD wallet index *i*′, that means 2^31^ + *i*.

インデックス番号を読みやすく表示するために、強化された子のインデックス番号はゼロから始まりますが、プライム記号が付きます。したがって、最初の通常の子鍵は0と表示されますが、最初の強化された子（インデックス0x80000000）は0'と表示されます。順番に、2番目の強化鍵のインデックスは0x80000001で、1'と表示されます。HDウォレットのインデックス*i*'は、2^31^ + *i*を意味します。

#### HD Wallet Key Identifier (Path)
#### HDウォレットの鍵識別子（パス）

Keys in an HD wallet are identified using a "path" naming convention, with each level of the tree separated by a slash (`/`) character (see Table 5-5). Private keys derived from the master private key start with `m`. Public keys derived from the master public key start with `M`. Therefore, the first child private key of the master private key is `m/0`. The first child public key is `M/0`. The second grandchild of the first child is `m/0/1`, and so on.

HDウォレット内の鍵は「パス」命名規則を使用して識別されます。ツリーの各レベルはスラッシュ（`/`）文字で区切られます（表5-5参照）。マスター秘密鍵から導出された秘密鍵は`m`で始まります。マスター公開鍵から導出された公開鍵は`M`で始まります。したがって、マスター秘密鍵の最初の子秘密鍵は`m/0`です。最初の子公開鍵は`M/0`です。最初の子の2番目の孫は`m/0/1`となります。

The "ancestry" of a key is read from right to left, until you reach the master key from which it was derived. For example, identifier `m/x/y/z` describes the key that is the *z*-th child of key `m/x/y`, which is the *y*-th child of key `m/x`, which is the *x*-th child of `m`.

鍵の「系譜」は、導出元のマスター鍵に到達するまで右から左に読みます。例えば、識別子`m/x/y/z`は、鍵`m/x/y`の*z*番目の子を表し、`m/x/y`は鍵`m/x`の*y*番目の子であり、`m/x`は`m`の*x*番目の子です。

**Table 5-5. HD wallet path examples**

**表5-5. HDウォレットのパスの例**

| HD path | Key described |
|---|---|
| HDパス | 鍵の説明 |
|---|---|
| m/0 | The first (0) child private key from the master private key (m) |
| m/0/0 | The first grandchild private key of the first child (m/0) |
| m/0'/0 | The first normal grandchild of the first hardened child (m/0') |
| m/1/0 | The first grandchild private key of the second child (m/1) |
| M/23/17/0/0 | The first great-great-grandchild public key of the first great-grandchild of the 18th grandchild of the 24th child |

### Navigating the HD Wallet Tree Structure
### HDウォレットのツリー構造のナビゲーション

The HD wallet tree structure is tremendously flexible. The flip side of this is that it also allows for unbounded complexity: each parent extended key can have four billion children—two billion normal children and two billion hardened children. Each of those children can have another four billion children, and so on. The tree can be as deep as you want, with a potentially infinite number of generations. With all that potential, it can become quite difficult to navigate these very large trees.

HDウォレットのツリー構造はきわめて柔軟です。その反面、無限の複雑さも許容します。各親拡張鍵は40億の子を持つことができ、そのうち20億が通常の子、20億が強化された子です。それらの子のそれぞれがさらに40億の子を持つことができ、以下同様に続きます。ツリーは潜在的に無限の世代を持ち、任意の深さにすることができます。これだけの可能性があると、これらの非常に大きなツリーをナビゲートすることはかなり困難になりえます。

Two BIPs offer a way to manage this potential complexity by creating standards for the structure of HD wallet trees. BIP-43 proposes the use of the first hardened child index as a special identifier that signifies the "purpose" of the tree structure. Based on BIP-43, an HD wallet should use only one level-one branch of the tree, with the index number defining the purpose of the wallet by identifying the structure and namespace of the rest of the tree. More specifically, an HD wallet using only branch `m/i′/...` is intended to signify a specific purpose, and that purpose is identified by index number *i*.

2つのBIPが、HDウォレットツリーの構造に関する標準を作ることでこの潜在的な複雑さを管理する方法を提示しています。BIP-43は、ツリー構造の「目的」を示す特別な識別子として、最初の強化子インデックスの使用を提案しています。BIP-43に基づき、HDウォレットはツリーの第1レベルのブランチを1つだけ使用し、インデックス番号がツリーの残りの構造と名前空間を特定することでウォレットの目的を定義します。より具体的には、ブランチ`m/i'/...`のみを使用するHDウォレットは特定の目的を示すことを意図しており、その目的はインデックス番号*i*によって識別されます。

Extending that specification, BIP-44 proposes a multicurrency, multiaccount structure signified by setting the "purpose" number to `44′`. All HD wallets following the BIP-44 structure are identified by the fact that they use only one branch of the tree: `m/44′/*`. BIP-44 specifies the structure as consisting of five predefined tree levels:

その仕様を拡張して、BIP-44は「目的」番号を`44'`に設定することで示されるマルチ通貨、マルチアカウント構造を提案しています。BIP-44の構造に従うすべてのHDウォレットは、ツリーの1つのブランチ`m/44'/*`のみを使用することで識別されます。BIP-44は、5つの事前定義されたツリーレベルで構成される構造を規定しています：

    m / purpose′ / coin_type′ / account′ / change / address_index

The first level, `purpose′`, is always set to `44′`. The second level, `coin_type′`, specifies the type of cryptocurrency coin, allowing for multicurrency HD wallets where each currency has its own subtree under the second level. There are several currencies defined in the standards document SLIP-0044; for example, Ethereum is `m/44′/60′`, Ethereum Classic is `m/44′/61′`, Bitcoin is `m/44′/0′`, and testnet for all currencies is `m/44′/1′`.

第1レベルの`purpose'`は常に`44'`に設定されます。第2レベルの`coin_type'`は暗号通貨の種類を指定し、各通貨が第2レベルの下に独自のサブツリーを持つマルチ通貨HDウォレットを可能にします。標準文書SLIP-0044にはいくつかの通貨が定義されています。例えば、イーサリアムは`m/44'/60'`、イーサリアムクラシックは`m/44'/61'`、ビットコインは`m/44'/0'`、すべての通貨のテストネットは`m/44'/1'`です。

The third level of the tree is `account′`, which allows users to subdivide their wallets into separate logical subaccounts for accounting or organizational purposes. For example, an HD wallet might contain two Ethereum accounts: `m/44′/60′/0′` and `m/44′/60′/1′`. Each account is the root of its own subtree.

ツリーの第3レベルは`account'`で、ユーザーが会計や組織の目的に合わせてウォレットを独立した論理的なサブアカウントに細分化できるようにします。例えば、HDウォレットには2つのイーサリアムアカウントが含まれることがあります：`m/44'/60'/0'`と`m/44'/60'/1'`。各アカウントはそれぞれのサブツリーのルートとなります。

Because BIP-44 was created originally for Bitcoin, it contains a "quirk" that isn't relevant in the Ethereum world. On the fourth level of the path, `change`, an HD wallet has two subtrees: one for creating receiving addresses and one for creating change addresses. Only the "receive" path is used in Ethereum, as there is no necessity for a change address like there is in Bitcoin. Note that whereas the previous levels used hardened derivation, this level uses normal derivation. This is to allow the account level of the tree to export extended public keys for use in a nonsecured environment.

BIP-44はもともとビットコイン用に作成されたため、イーサリアムの世界では関係のない「癖」が含まれています。パスの第4レベルの`change`では、HDウォレットは2つのサブツリーを持ちます。1つは受信アドレスの作成用、もう1つはおつりアドレスの作成用です。イーサリアムではビットコインのようなおつりアドレスの必要がないため、「受信」パスのみが使用されます。前のレベルが強化導出を使用していたのに対し、このレベルでは通常導出が使用されることに注意してください。これは、ツリーのアカウントレベルが安全でない環境での使用のために拡張公開鍵をエクスポートできるようにするためです。

Usable addresses are derived by the HD wallet as children of the fourth level, making the fifth level of the tree the `address_index`. For example, the third receiving address for Ethereum payments in the primary account would be `M/44′/60′/0′/0/2`. Table 5-6 shows a few more examples.

利用可能なアドレスは、HDウォレットによって第4レベルの子として導出され、ツリーの第5レベルが`address_index`になります。例えば、プライマリアカウントでのイーサリアム支払い用の3番目の受信アドレスは`M/44'/60'/0'/0/2`となります。表5-6にさらにいくつかの例を示します。

**Table 5-6. BIP-44 HD wallet structure examples**

**表5-6. BIP-44 HDウォレット構造の例**

| HD path | Key described |
|---|---|
| HDパス | 鍵の説明 |
|---|---|
| M/44′/60′/0′/0/2 | The third receiving public key for the primary Ethereum account |
| M/44′/0′/3′/1/14 | The 15th change-address public key for the fourth Bitcoin account |
| m/44′/2′/0′/0/1 | The second private key in the Litecoin main account, for signing transactions |

## Security
## セキュリティ

Let's start by introducing the concept of security versus ease of recovery. Taking these concepts to the extreme: what's the most secure seed? It's the one that no one can recover, not even you. So if the seed is created and all copies (physical or digital) are destroyed, that's the most secure seed in the world. Not great, as you wouldn't be able to recover it, but it's technically the most secure.

まず、セキュリティとリカバリの容易さの概念を紹介しましょう。これらの概念を極端にとらえると、最も安全なシードとは何でしょうか？それは誰もリカバリできないシード、自分自身でさえもリカバリできないシードです。つまり、シードが作成され、すべてのコピー（物理的・デジタル的）が破壊されたなら、それは世界で最も安全なシードです。リカバリできないので実用的ではありませんが、技術的には最も安全です。

On the flip side, for ease of recovery, what's the easiest seed to recover? One that has the seed phrase written everywhere, like getting it tattooed on your body, in plain sight. That seed will be super easy to recover but not secure at all.

逆に、リカバリの容易さについて言えば、最もリカバリしやすいシードとは何でしょうか？シードフレーズがあらゆるところに書かれている、例えば体に刺青として見える場所に入れてあるようなものです。そのシードはリカバリが非常に簡単ですが、まったく安全ではありません。

Any choice you make for your operational security (OpSec) in self-custody will likely increase either the security or the ease of recovery of your seed phrase. Increasing security typically reduces ease of recovery, and vice versa. Sometimes, you may end up reducing both, which should be avoided.

セルフカストディにおける運用セキュリティ（OpSec）のためにあなたが行うあらゆる選択は、シードフレーズのセキュリティまたはリカバリの容易さのいずれかを向上させる可能性が高いです。セキュリティを高めると通常はリカバリの容易さが低下し、その逆も同様です。場合によっては両方を低下させてしまうこともあり、これは避けるべきです。

Even with a high-security system, no setup is 100% secure. You can do everything in your power to create a perfect system, but there will still be vulnerabilities. One of the most interesting is private-key collisions: essentially generating a seed that's already been used. Since seeds in hardware wallets are generated offline and there's no database of generated seeds, it's technically possible to generate the same wallet twice. The chances of this happening are astronomically small (you're more likely to win the lottery twice in a row), but it's still a possibility.

高セキュリティのシステムであっても、100%安全な設定は存在しません。完璧なシステムを作るためにできる限りのことをしても、脆弱性は依然として存在します。最も興味深いものの1つは秘密鍵の衝突です。本質的には、すでに使用されたシードを生成してしまうことです。ハードウェアウォレットのシードはオフラインで生成され、生成済みシードのデータベースは存在しないため、技術的には同じウォレットを2回生成することが可能です。これが起こる確率は天文学的に小さいですが（宝くじに2回連続で当たる確率よりも低い）、可能性としては存在します。

> **Warning**
>
> Often, there's no urgency in seed security. Either your seed has been stolen, in which case you're already in trouble, or it hasn't. This is especially true for Bitcoin wallets. For Ethereum, it is still the case, but there are situations where acting fast can save funds—for example, removing approvals to dangerous smart contracts. If you receive any urgent messages about your seed, it's probably a scam.

> **警告**
>
> シードのセキュリティに関しては、緊急性がないことがほとんどです。シードが盗まれていればすでに問題が発生していますし、盗まれていなければ問題はありません。これは特にビットコインウォレットに当てはまります。イーサリアムでも同様ですが、迅速な行動で資金を救える状況もあります。例えば、危険なスマートコントラクトへの承認を取り消す場合です。シードに関する緊急メッセージを受け取った場合、それはおそらく詐欺です。

Complex security mechanisms for hiding your seed are not a best practice. Although they may seem foolproof at first, professionals in the field can often recover these types of seeds with the right tools. And if it's so complex that even professionals can't recover it, there's a good chance you won't be able to when needed.

シードを隠すための複雑なセキュリティメカニズムはベストプラクティスではありません。一見完璧に見えるかもしれませんが、その分野の専門家は適切なツールを使えばこの種のシードをリカバリできることが多いです。そして、専門家でもリカバリできないほど複雑であれば、必要なときに自分自身でもリカバリできない可能性が高いです。

Another non–best practice is relying on obscurity for security. Your system should have as few "secret" components as possible, with the seed itself being the main one. If revealing parts of your system causes it to collapse, it's not secure.

もう1つのベストプラクティスではないことは、セキュリティを隠蔽に頼ることです。システムには「秘密」のコンポーネントをできるだけ少なくし、シード自体を主要なものとすべきです。システムの一部を公開するとシステムが崩壊するのであれば、それは安全ではありません。

A best practice is to follow what most others do. Trying to invent new systems or, worse, creating everything from scratch is wrong. It's not secure, and the majority of people don't have the technical skills to do it. Keep things simple. Simplicity is absolutely a best practice.

ベストプラクティスは、他の多くの人がやっていることに従うことです。新しいシステムを発明しようとしたり、さらに悪いことにすべてをゼロから作ろうとするのは間違いです。安全ではありませんし、ほとんどの人にはそれを行う技術的スキルがありません。シンプルに保ちましょう。シンプルさは間違いなくベストプラクティスです。

Making a backup of your seed is probably the most important best practice. Whether it's a hardware wallet or a browser wallet, a backup is essential. Backup storage should (a) withstand natural disasters, (b) be geographically separate from your hardware wallet, (c) be in a secure place, and (d) have tamper-evident packaging. Dividing your seed across multiple pieces of paper is not a best practice. It gives a false sense of security.

シードのバックアップを作成することは、おそらく最も重要なベストプラクティスです。ハードウェアウォレットであれブラウザウォレットであれ、バックアップは不可欠です。バックアップの保管場所は、(a) 自然災害に耐えられること、(b) ハードウェアウォレットとは地理的に離れていること、(c) 安全な場所であること、(d) 改ざん防止のパッケージであること、が求められます。シードを複数の紙に分割することはベストプラクティスではありません。誤った安心感を与えるだけです。

> **Tip**
>
> If you don't have a secure place to store your seed, consider using a passphrase. The passphrase adds an extra layer of protection by being combined with your seed during the key-generation process. You can even store the passphrase digitally since it's useless without the seed. If someone gets your seed but not your passphrase, they won't be able to access your funds for a certain amount of time; this is because the passphrase can be brute-forced if the attacker has the seed.

> **ヒント**
>
> シードを保管する安全な場所がない場合は、パスフレーズの使用を検討してください。パスフレーズは鍵生成プロセス中にシードと組み合わされることで、追加の保護層を提供します。パスフレーズはシードなしでは無意味なので、デジタルで保存することもできます。誰かがシードを入手してもパスフレーズを入手しなければ、一定期間は資金にアクセスできません。これは、攻撃者がシードを持っていればパスフレーズをブルートフォースで解読できるためです。

Everyone's needs are different, and their security requirements will vary accordingly. But you should always follow best practices. Your needs may change over time, so stay aware and adjust your OpSec if needed.

人によってニーズは異なり、セキュリティ要件もそれに応じて変わります。しかし、常にベストプラクティスに従うべきです。ニーズは時間とともに変化する可能性があるため、常に注意を払い、必要に応じてOpSecを調整してください。

After setting up your hardware wallet, test your ability to recover the seed. Do this at least once every 12 months, ensuring that your backup works and is accessible.

ハードウェアウォレットをセットアップした後、シードをリカバリする能力をテストしてください。少なくとも12か月に1回はこれを行い、バックアップが機能し、アクセス可能であることを確認してください。

What does a secure system look like? A trusted hardware wallet (like Trezor), at least one safe backup (never saved digitally), and a plan for inheritance in case something happens to you.

安全なシステムとはどのようなものでしょうか？信頼できるハードウェアウォレット（Trezorなど）、少なくとも1つの安全なバックアップ（デジタルで保存しないこと）、そしてあなたに何かあった場合の相続計画です。

> **Note**
>
> Inheritance is a very complicated topic. We recommend reading *Cryptoasset Inheritance Planning: A Simple Guide for Owners* by Pamela Morgan (Merkle Bloom).

> **注記**
>
> 相続は非常に複雑なトピックです。パメラ・モーガン著『*Cryptoasset Inheritance Planning: A Simple Guide for Owners*』（Merkle Bloom）を読むことをお勧めします。

## Improving on User Experience
## ユーザーエクスペリエンスの改善

As we mentioned earlier, at a high level, a wallet is a software application that serves as the primary user interface to Ethereum. So for most of Ethereum's users, the wallet is most of the user experience. For years, it has not really been improved. For example, the most popular browser wallet at the time of writing is MetaMask, which has not evolved that much since its inception; a close second, Rabby, has recently emerged. We will now examine a few updates to wallets that could drastically improve the user experience.

前述のように、広義にはウォレットとはイーサリアムへの主要なユーザーインターフェイスとして機能するソフトウェアアプリケーションです。そのため、イーサリアムのユーザーの大部分にとって、ウォレットがユーザーエクスペリエンスのほぼすべてです。長年にわたり、これは本当に改善されてきませんでした。例えば、執筆時点で最も人気のあるブラウザウォレットはMetaMaskですが、誕生以来それほど進化していません。僅差の2番手としてRabbyが最近登場しました。ここでは、ユーザーエクスペリエンスを劇的に改善しうるウォレットのいくつかのアップデートについて検討します。

### Account Abstraction
### アカウントアブストラクション

Account abstraction (AA) on Ethereum is a way to make user accounts more flexible and easier to use. Normally, there are two types of accounts in Ethereum, as described in Chapter 2: EOAs and smart contract accounts. AA combines the benefits of both types. It allows regular accounts (EOAs) to behave more like smart contracts, meaning users can set up custom rules for how their accounts work, such as adding security features or allowing multiple people to sign transactions.

イーサリアムにおけるアカウントアブストラクション（AA）は、ユーザーアカウントをより柔軟で使いやすくするための方法です。通常、第2章で説明したように、イーサリアムにはEOAとスマートコントラクトアカウントの2種類のアカウントがあります。AAは両方の利点を組み合わせます。通常のアカウント（EOA）がスマートコントラクトのように振る舞えるようになり、セキュリティ機能の追加や複数人によるトランザクション署名の許可など、アカウントの動作に対してカスタムルールを設定できます。

With AA, Ethereum can become more user-friendly and flexible. For example, you could recover a lost account without relying solely on a private key, or you could pay transaction fees in any token, not just ether.

AAにより、イーサリアムはより使いやすく柔軟になります。例えば、秘密鍵だけに頼らずに紛失したアカウントをリカバリしたり、Etherだけでなく任意のトークンでトランザクション手数料を支払ったりできるようになります。

There have been multiple proposals to implement AA. The main distinction is that one group of proposals tried to implement AA without changing the Ethereum protocol. Another group of proposals, which will be implemented in the Pectra upgrade, will end up changing the Ethereum protocol.

AAを実装するための提案は複数あります。主な区別は、一方の提案グループがイーサリアムプロトコルを変更せずにAAを実装しようとしたのに対し、もう一方の提案グループはPectraアップグレードで実装される予定であり、イーサリアムプロトコル自体を変更することになるという点です。

Let's look at the main EIPs and Ethereum Requests for Comments (ERCs) for AA. Keep in mind that these proposals are evolving rapidly, and by the time this book is published, the AA landscape may have changed significantly. Nevertheless, it's still useful to explore what has been implemented and what is planned for the near future.

AAに関する主なEIPとEthereum Requests for Comments（ERC）を見ていきましょう。これらの提案は急速に進化しており、本書が出版される頃にはAAの状況は大きく変わっている可能性があることに留意してください。それでも、何が実装され、近い将来何が計画されているかを探ることは有益です。

> **Tip**
>
> It is important to understand the difference between an ERC, an EIP, and a Rollup Improvement Proposal (RIP). Essentially, EIPs and RIPs are improvements that center on changes in the Ethereum networks, whereas ERCs are application-related changes that do not have any impact on core network capability.

> **ヒント**
>
> ERC、EIP、およびRollup Improvement Proposal（RIP）の違いを理解することが重要です。基本的に、EIPとRIPはイーサリアムネットワークの変更を中心とした改善であるのに対し、ERCはコアネットワークの機能に影響を与えないアプリケーション関連の変更です。

#### ERC-4337

ERC-4337 is an advancement in the Ethereum blockchain that aims to make user accounts more versatile, secure, and user-friendly. Unlike typical upgrades that alter the Ethereum protocol, ERC-4337 introduces new functionality through smart contracts and off-chain components. As of September 2024, the primary on-chain implementation of AA is ERC-4337.

ERC-4337は、ユーザーアカウントをより多機能、安全、使いやすくすることを目的としたイーサリアムブロックチェーンの進歩です。イーサリアムプロトコルを変更する一般的なアップグレードとは異なり、ERC-4337はスマートコントラクトとオフチェーンコンポーネントを通じて新しい機能を導入します。2024年9月時点で、AAの主要なオンチェーン実装はERC-4337です。

As we said in Chapter 2, traditional Ethereum accounts are divided into two types: EOAs, controlled solely by private keys, and contract accounts, which operate through smart contracts. EOAs dominate user wallets today because they are simple and economical; however, they are also limited in functionality and prone to security risks. Losing a private key can mean permanent loss of funds, and EOAs are not customizable for security features like multisignature setups or account-recovery options. Contract accounts can incorporate these security measures and more, yet their complexity and higher transaction fees have prevented their widespread use by everyday users. ERC-4337 overcomes this by enabling EOAs to function as smart contracts, merging the simplicity of EOAs with the security and flexibility of contract accounts.

第2章で述べたように、従来のイーサリアムアカウントは2種類に分けられます。秘密鍵のみで制御されるEOAと、スマートコントラクトを通じて動作するコントラクトアカウントです。EOAはシンプルで経済的であるため、現在ユーザーウォレットの主流です。しかし、機能が限定的であり、セキュリティリスクにさらされやすいです。秘密鍵を紛失すると資金の永久的な喪失を意味する可能性があり、EOAはマルチシグ設定やアカウントリカバリオプションなどのセキュリティ機能のカスタマイズができません。コントラクトアカウントはこれらのセキュリティ対策やそれ以上のものを組み込めますが、その複雑さとより高いトランザクション手数料が一般ユーザーへの普及を妨げてきました。ERC-4337は、EOAがスマートコントラクトとして機能できるようにすることでこれを克服し、EOAのシンプルさとコントラクトアカウントのセキュリティおよび柔軟性を融合させます。

The implementation of ERC-4337 introduces *UserOperations* to handle transactions differently, as shown in Figure 5-5. Rather than directly broadcasting each transaction to the blockchain, users submit UserOperations to a high-level mempool, where transactions are temporarily stored. Special participants, known as *bundlers*, collect and process these UserOperations, packaging them into a single Ethereum transaction. This process reduces network congestion and allows multiple operations to be processed in a more efficient, bundled manner. ERC-4337 also establishes a new role called *paymasters*. Typically, Ethereum transactions require the payment of gas fees in ETH, but paymasters make it possible for users to cover gas fees with alternative tokens or even to have a third-party sponsor pay the fees on their behalf. This shift eliminates a significant barrier, especially for newcomers who may not hold ETH, making the Ethereum network more inclusive and accessible.

ERC-4337の実装では、図5-5に示すように、トランザクションを異なる方法で処理する*UserOperation*が導入されます。各トランザクションを直接ブロックチェーンにブロードキャストするのではなく、ユーザーはUserOperationを高レベルのメンプールに送信し、そこでトランザクションは一時的に保存されます。*バンドラー*と呼ばれる特別な参加者がこれらのUserOperationを収集・処理し、1つのイーサリアムトランザクションにパッケージングします。このプロセスはネットワークの輻輳を軽減し、複数のオペレーションをより効率的にバンドルして処理できるようにします。ERC-4337はまた、*ペイマスター*と呼ばれる新しい役割を確立します。通常、イーサリアムトランザクションではETHでガス代を支払う必要がありますが、ペイマスターにより、ユーザーは代替トークンでガス代を支払ったり、第三者のスポンサーに代わりに手数料を支払ってもらったりすることが可能になります。この変革は、特にETHを保有していない新規ユーザーにとっての大きな障壁を取り除き、イーサリアムネットワークをより包括的でアクセスしやすいものにします。

![ERC-4337 implementation diagram](images/ch5/maet_0505.png)

Figure 5-5. ERC-4337 implementation diagram

図5-5. ERC-4337の実装図

Instead of using the traditional public mempool, which hosts pending transactions for EOAs, UserOperations are sent to a specialized *UserOperation mempool*: a higher-level mempool specifically designed for these operations. Bundlers monitor the UserOperation mempool, collecting multiple UserOperations to package them into a single "classic" transaction. They start by verifying each UserOperation's validity through the EntryPoint methods. After validation, the bundler submits this bundled transaction directly to the next proposed block, bypassing the regular mempool. Bundlers can either act as block builders themselves or collaborate with block builders to add the transaction to the blockchain.

EOAの保留中のトランザクションをホストする従来のパブリックメンプールを使用する代わりに、UserOperationは専用の*UserOperationメンプール*に送信されます。これはこれらのオペレーション専用に設計された高レベルのメンプールです。バンドラーはUserOperationメンプールを監視し、複数のUserOperationを収集して1つの「従来型」トランザクションにパッケージングします。まず、EntryPointメソッドを通じて各UserOperationの有効性を検証します。検証後、バンドラーはこのバンドルされたトランザクションを通常のメンプールをバイパスして、次の提案ブロックに直接送信します。バンドラーは自らブロックビルダーとして機能することも、ブロックビルダーと連携してトランザクションをブロックチェーンに追加することもできます。

#### EIP-2938

While ERC-4337 focuses on AA at a high level via smart contracts without changing Ethereum's core, EIP-2938 goes a step further by proposing that AA be embedded within the protocol layer itself. This lower-level approach allows for even more direct and flexible interactions among users, smart contracts, and applications by fundamentally changing how the EVM treats accounts. Through EIP-2938, users could handle operations without traditional EOAs, removing reliance on private-key-based accounts and enabling a greater diversity of account management systems, such as multisignature accounts or social recovery accounts, directly on Ethereum's protocol level.

ERC-4337がイーサリアムのコアを変更せずにスマートコントラクトを通じて高レベルでAAに焦点を当てているのに対し、EIP-2938はさらに一歩進んで、AAをプロトコル層自体に組み込むことを提案しています。この低レベルのアプローチは、EVMがアカウントを扱う方法を根本的に変更することで、ユーザー、スマートコントラクト、アプリケーション間のより直接的で柔軟なインタラクションを可能にします。EIP-2938により、ユーザーは従来のEOAなしでオペレーションを処理でき、秘密鍵ベースのアカウントへの依存を排除し、マルチシグアカウントやソーシャルリカバリアカウントなど、より多様なアカウント管理システムをイーサリアムのプロトコルレベルで直接実現できます。

The main difference between EIP-2938 and some existing AA proposals lies in the focus on integrating abstraction directly into the protocol, rather than layering it on top. With EIP-2938, Ethereum would support "operations" rather than "transactions," where each operation could represent a more versatile, customizable transaction type. EIP-2938 can redefine Ethereum's transactions as programmable objects, supporting a broader spectrum of use cases. By treating accounts and transactions as inherently programmable, it expands Ethereum's utility beyond standard payments and contract interactions, fitting perfectly with the increasingly complex applications being built on the network.

EIP-2938と既存のAA提案の主な違いは、アブストラクションをプロトコルの上にレイヤーとして載せるのではなく、プロトコルに直接統合することに焦点を当てている点にあります。EIP-2938により、イーサリアムは「トランザクション」ではなく「オペレーション」をサポートし、各オペレーションはより多機能でカスタマイズ可能なトランザクションタイプを表すことができます。EIP-2938はイーサリアムのトランザクションをプログラム可能なオブジェクトとして再定義し、より広範なユースケースをサポートできます。アカウントとトランザクションを本質的にプログラム可能なものとして扱うことで、標準的な支払いやコントラクトとのインタラクションを超えてイーサリアムの有用性を拡張し、ネットワーク上に構築されるますます複雑なアプリケーションに完璧に適合します。

#### RIP-7560

The RIP-7560 proposal integrates EIP-2938 and ERC-4337 into a unified approach for native AA, splitting Ethereum's transaction scope into validation, execution, and post-transaction steps. By separating transaction validation into distinct processes for authorization and payment of gas fees, it enables one contract to sponsor gas fees for another account's transaction. This approach maintains compatibility with ERC-4337's ecosystem while working toward the goal of fully native AA.

RIP-7560提案は、EIP-2938とERC-4337をネイティブAAのための統一的なアプローチに統合し、イーサリアムのトランザクションスコープを検証、実行、トランザクション後のステップに分割します。トランザクションの検証を認可とガス代の支払いの別々のプロセスに分離することで、あるコントラクトが別のアカウントのトランザクションのガス代をスポンサーすることを可能にします。このアプローチは、完全なネイティブAAの目標に向かいながら、ERC-4337のエコシステムとの互換性を維持します。

ERC-4337 introduces AA at the application level, but it comes with limitations due to its out-of-protocol design. These drawbacks include extra gas costs, limited censorship resistance, a dependency on nonstandard RPC methods, and restrictions that limit compatibility with existing contract expectations. Native AA, as proposed in EIP-2938, presents a more robust alternative by building these features directly into the protocol. However, EIP-2938 doesn't fully align with ERC-4337's structure, which has been widely tested and implemented without protocol changes.

ERC-4337はアプリケーションレベルでAAを導入しますが、プロトコル外の設計であるため制限があります。これらの欠点には、追加のガスコスト、限定的な検閲耐性、非標準RPCメソッドへの依存、既存のコントラクトの期待との互換性を制限する制約が含まれます。EIP-2938で提案されたネイティブAAは、これらの機能をプロトコルに直接組み込むことで、より堅牢な代替手段を提示します。しかし、EIP-2938はプロトコル変更なしで広くテスト・実装されてきたERC-4337の構造と完全には整合しません。

By combining EIP-2938's built-in protocol-level features with the practical insights gained from ERC-4337, this proposal brings together the best of both approaches. This hybrid approach aims to lower gas costs, improve the reliability of transactions by making them more resistant to censorship, and ensure compatibility with current and future Ethereum contracts. Gradually moving from EOAs to smart contract accounts would also reduce risks tied to private keys, making Ethereum more secure and easier to use. Importantly, this setup ensures that those already using ERC-4337 can smoothly adopt these new features.

EIP-2938の組み込みプロトコルレベル機能とERC-4337から得られた実践的な知見を組み合わせることで、この提案は両方のアプローチの長所を統合します。このハイブリッドアプローチは、ガスコストの削減、検閲耐性の向上によるトランザクションの信頼性の改善、現在および将来のイーサリアムコントラクトとの互換性の確保を目指しています。EOAからスマートコントラクトアカウントへの段階的な移行は、秘密鍵に関連するリスクも軽減し、イーサリアムをより安全で使いやすくします。重要なことに、このセットアップにより、すでにERC-4337を使用しているユーザーがこれらの新機能をスムーズに採用できることが保証されます。

Figure 5-6 represents the transaction flow for AA as outlined in RIP-7560. The process incorporates several key contracts that handle validation, deployment, and execution, creating a streamlined, modular approach to managing user accounts and transactions on the Ethereum blockchain.

図5-6は、RIP-7560で概説されたAAのトランザクションフローを表しています。このプロセスは、検証、デプロイメント、実行を処理するいくつかの主要なコントラクトを組み込み、イーサリアムブロックチェーン上でのユーザーアカウントとトランザクションの管理に対する効率的でモジュラーなアプローチを実現します。

![RIP-7560 transaction flow](images/ch5/maet_0506.png)

Figure 5-6. RIP-7560 transaction flow

図5-6. RIP-7560のトランザクションフロー

The flow begins with a nonce check by the Nonce Manager Contract to ensure that the transaction is unique and hasn't been replayed. This is a crucial step for transaction integrity because it prevents double-spending or accidental repeats. If the nonce is valid, the system moves forward; otherwise, the transaction is halted.

フローは、Nonce Managerコントラクトによるナンスチェックから始まり、トランザクションが一意であり、リプレイされていないことを確認します。これは二重支払いや偶発的な繰り返しを防ぐため、トランザクションの整合性にとって重要なステップです。ナンスが有効であればシステムは先に進み、そうでなければトランザクションは停止されます。

Next, the process checks if the user's Account Contract (a smart wallet) already exists. If not, the Deployer Contract steps in to create this wallet, allowing the user to participate in transactions. Once it is deployed, or if it is already in place, the Account Contract itself performs a validation check to confirm that the transaction is legitimate and aligns with the contract's logic. This ensures that only authorized actions proceed, adding a layer of security and customization to each user's wallet.

次に、プロセスはユーザーのAccountコントラクト（スマートウォレット）がすでに存在するかどうかをチェックします。存在しない場合、Deployerコントラクトがこのウォレットを作成し、ユーザーがトランザクションに参加できるようにします。デプロイされた後、またはすでに存在する場合、Accountコントラクト自体が検証チェックを実行し、トランザクションが正当であり、コントラクトのロジックに整合していることを確認します。これにより、承認されたアクションのみが実行され、各ユーザーのウォレットにセキュリティとカスタマイズの層が追加されます。

An interesting feature of this flow is the optional involvement of a Paymaster Contract. If specified, this contract can cover the gas fees for the transaction or offer alternative payment methods. When a paymaster is involved, it undergoes its own validation process to ensure it can legitimately cover the transaction costs. This flexibility allows for sponsorship models and potentially reduces the burden of transaction fees on users.

このフローの興味深い特徴は、Paymasterコントラクトのオプション的な関与です。指定された場合、このコントラクトはトランザクションのガス代を負担したり、代替の支払い方法を提供したりできます。ペイマスターが関与する場合、トランザクションコストを正当に負担できることを確認するために独自の検証プロセスを経ます。この柔軟性により、スポンサーシップモデルが可能になり、ユーザーに対するトランザクション手数料の負担を軽減できる可能性があります。

Once all validations are complete, the Ethereum Execution Layer begins processing the transaction. During execution, an Execution Frame is used to handle the transaction details and monitor its progression. After execution, if a paymaster was involved, it performs any necessary postprocessing to finalize the transaction sponsorship.

すべての検証が完了すると、イーサリアム実行層がトランザクションの処理を開始します。実行中は、Execution Frameがトランザクションの詳細を処理し、その進行を監視するために使用されます。実行後、ペイマスターが関与していた場合、トランザクションのスポンサーシップを完了するために必要なポストプロセッシングを実行します。

#### EIP-5806

EIP-5806 introduces a new transaction type, enabling EOAs to run custom code through a "delegate call" mechanism.

EIP-5806は新しいトランザクションタイプを導入し、「デリゲートコール」メカニズムを通じてEOAがカスタムコードを実行できるようにします。

Currently, EOAs can only deploy contracts or send "call" transactions, limiting user interactions with the blockchain. This restriction affects usability since EOAs cannot perform tasks like batching multiple actions into one transaction or executing complex operations. While AA could solve these issues, its adoption path remains uncertain, and not all users can migrate because of costs and nontransferable asset custody.

現在、EOAはコントラクトのデプロイまたは「コール」トランザクションの送信のみが可能であり、ブロックチェーンとのユーザーインタラクションが制限されています。EOAは複数のアクションを1つのトランザクションにバッチ処理したり、複雑なオペレーションを実行したりするタスクを実行できないため、この制限はユーザビリティに影響します。AAがこれらの問題を解決できる可能性はありますが、その採用経路は不透明であり、コストや譲渡不可能な資産のカストディのためにすべてのユーザーが移行できるわけではありません。

This proposal offers a straightforward way for EOAs to execute custom code with minimal EVM changes and familiar security standards. By allowing EOAs to delegate calls to specific contracts, users gain more control and flexibility, enabling complex operations like multicall batching or secure token transfers. Unlike other AA proposals, this approach aims to improve EOA user experience without replacing existing abstraction methods, making it an accessible option for enhanced EOA functionality in the near future.

この提案は、最小限のEVM変更と馴染みのあるセキュリティ標準で、EOAがカスタムコードを実行するための簡単な方法を提供します。EOAが特定のコントラクトにコールをデリゲートできるようにすることで、ユーザーはより多くの制御と柔軟性を得て、マルチコールバッチングや安全なトークン転送などの複雑なオペレーションが可能になります。他のAA提案とは異なり、このアプローチは既存のアブストラクション方法を置き換えることなくEOAのユーザーエクスペリエンスを改善することを目指しており、近い将来のEOA機能強化のためのアクセスしやすいオプションとなっています。

#### EIP-3074

EIP-3074 introduces two opcodes, `AUTH` and `AUTHCALL`, to allow EOAs to delegate control of their transactions to an "invoker" contract. The user signs a message containing the invoker and a commit (a hash of transaction values), ensuring that the invoker only processes authorized transactions. Replay protection is handled by the invoker, and users must trust this contract to avoid malicious behavior. This proposal improves transaction batching and enables flexible account delegation.

EIP-3074は、EOAが「インボーカー」コントラクトにトランザクションの制御をデリゲートできるようにするために、`AUTH`と`AUTHCALL`の2つのオペコードを導入します。ユーザーはインボーカーとコミット（トランザクション値のハッシュ）を含むメッセージに署名し、インボーカーが承認されたトランザクションのみを処理することを保証します。リプレイ保護はインボーカーが処理し、ユーザーは悪意のある動作を避けるためにこのコントラクトを信頼する必要があります。この提案はトランザクションのバッチ処理を改善し、柔軟なアカウントのデリゲーションを可能にします。

`AUTH` lets users grant a smart contract permission to act on their behalf. It uses a digital signature (ECDSA) to verify this authorization, then stores the user's address for future transactions. `AUTHCALL` allows the authorized smart contract to perform transactions, such as sending tokens or interacting with other contracts. For example, if you want to swap 10 DAI for ETH, you can authorize the invoker (using `AUTH`) with one signature. The invoker will use `AUTHCALL` to approve Uniswap to spend your DAI and then execute the swap.

`AUTH`は、ユーザーがスマートコントラクトに自分の代わりに行動する許可を与えることを可能にします。デジタル署名（ECDSA）を使用してこの認可を検証し、将来のトランザクションのためにユーザーのアドレスを保存します。`AUTHCALL`は、認可されたスマートコントラクトがトークンの送信や他のコントラクトとのインタラクションなどのトランザクションを実行できるようにします。例えば、10 DAIをETHにスワップしたい場合、1つの署名でインボーカーを認可（`AUTH`を使用）できます。インボーカーは`AUTHCALL`を使用してUniswapにDAIの使用を承認し、その後スワップを実行します。

Initially, replay protection and fields like value, gas, and other `AUTHCALL` arguments were also signed. The design evolved to delegate these tasks to the invoker contract, making it crucial for users to trust the invoker. Users can "commit" to particular call properties by hashing them. The invoker validates only if the committed values, such as the nonce for replay protection, match the user's commitment, as shown in Figure 5-7. This ensures that the invoker processes exactly what the user authorized.

当初、リプレイ保護やvalue、gas、その他の`AUTHCALL`引数などのフィールドも署名されていました。設計はこれらのタスクをインボーカーコントラクトにデリゲートするように進化し、ユーザーがインボーカーを信頼することがより重要になりました。ユーザーは特定のコールプロパティをハッシュ化することで「コミット」できます。インボーカーは、図5-7に示すように、リプレイ保護用のナンスなどのコミットされた値がユーザーのコミットメントと一致する場合のみ検証します。これにより、インボーカーがユーザーが認可したものだけを正確に処理することが保証されます。

![EIP-3074 commitment validation](images/ch5/maet_0507.png)

Figure 5-7. EIP-3074 commitment validation

図5-7. EIP-3074のコミットメント検証

The commit hash enables invokers to enforce various rules, such as allowing parallel nonces or bundling multiple calls under one signature. This enables multicall flows, such as consolidating an ERC-20 approve-transfer into a single transaction, as seen in Figure 5-8.

コミットハッシュにより、インボーカーは並列ナンスの許可や1つの署名の下での複数コールのバンドルなど、さまざまなルールを適用できます。これにより、図5-8に見られるように、ERC-20のapprove-transferを1つのトランザクションに統合するなどのマルチコールフローが可能になります。

![EIP-3074 multicall flow](images/ch5/maet_0508.png)

Figure 5-8. EIP-3074 multicall flow

図5-8. EIP-3074のマルチコールフロー

Additionally, it supports delegating control of the EOA to other keys by signing a commit message with the delegate's address and an access policy, which the invoker verifies before relaying calls on behalf of the EOA, as seen in Figure 5-9.

さらに、デリゲートのアドレスとアクセスポリシーを含むコミットメッセージに署名することで、EOAの制御を他の鍵にデリゲートすることもサポートしています。インボーカーは、図5-9に示すように、EOAの代わりにコールを中継する前にこれを検証します。

![EIP-3074 delegation flow](images/ch5/maet_0509.png)

Figure 5-9. EIP-3074 delegation flow

図5-9. EIP-3074のデリゲーションフロー

#### EIP-5003

EIP-5003 introduces the `AUTHUSURP` opcode, which allows code deployment at an address authorized through EIP-3074, effectively removing the original EOA's signing key (when used with EIP-3607). Traditional EOAs control a lot of value on Ethereum but face limitations. There's no easy way to rotate keys, batch transactions for efficiency, or enable gas sponsorship without holding ETH. Contract accounts and AA address these issues, allowing users to customize security features, authentication methods, spending limits, key rotation, social recovery, and more. However, these benefits are mostly limited to users who actively adopt new standards through smart contract wallets and app-layer solutions, such as those proposed by ERC-4337. This leaves a substantial number of existing users, who have relied on EOAs since Ethereum's inception, with limited security and usability improvements.

EIP-5003は`AUTHUSURP`オペコードを導入します。これにより、EIP-3074を通じて認可されたアドレスにコードをデプロイし、（EIP-3607と併用した場合に）元のEOAの署名鍵を実質的に無効化できます。従来のEOAはイーサリアム上で多くの価値を管理していますが、制限に直面しています。鍵のローテーション、効率のためのトランザクションバッチ処理、ETHを保持せずにガススポンサーシップを有効にする簡単な方法がありません。コントラクトアカウントとAAはこれらの問題に対処し、ユーザーがセキュリティ機能、認証方法、支出制限、鍵のローテーション、ソーシャルリカバリなどをカスタマイズできるようにします。しかし、これらの利点は主に、ERC-4337で提案されているようなスマートコントラクトウォレットやアプリケーション層のソリューションを通じて新しい標準を積極的に採用するユーザーに限定されています。これにより、イーサリアムの誕生以来EOAに依存してきた相当数の既存ユーザーは、セキュリティとユーザビリティの改善が限定的なままとなっています。

While EIP-3074 offers an initial solution by enabling EOAs to delegate signing authority to a contract account, it stops short of allowing the EOA to completely revoke this original signing key. This gap introduces a security risk: even with delegated authority, the primary private key remains a potential vulnerability. If compromised, the entire account remains at risk, as there is currently no revocation option for an exposed private key. If a user's private key is leaked, either by accident or through a malicious attack, the only option is to create a new wallet and painstakingly migrate assets individually, an expensive and often incomplete process due to the immovability of certain assets within existing smart contracts.

EIP-3074はEOAがコントラクトアカウントに署名権限をデリゲートできるようにすることで初期的な解決策を提供しますが、EOAがこの元の署名鍵を完全に取り消すことまでは許可しません。このギャップはセキュリティリスクを生みます。デリゲートされた権限があっても、プライマリ秘密鍵は潜在的な脆弱性として残ります。危殆化した場合、露出した秘密鍵の取り消しオプションが現在存在しないため、アカウント全体がリスクにさらされたままです。ユーザーの秘密鍵が偶発的またはの悪意ある攻撃によって漏洩した場合、唯一のオプションは新しいウォレットを作成し、資産を個別に苦労して移行することですが、既存のスマートコントラクト内の特定の資産は移動できないため、高価で不完全なプロセスとなりがちです。

With this EIP, `AUTHUSURP` provides a secure transition path for EOA holders. It allows EOAs to fully transfer control to a smart contract, removing the original key's authority and thereby eliminating it as a security threat.

このEIPにより、`AUTHUSURP`はEOA保有者に安全な移行パスを提供します。EOAがスマートコントラクトに完全に制御を移譲し、元の鍵の権限を削除することで、セキュリティ上の脅威を排除できます。

#### EIP-7702

EIP-7702 is the main AA EIP expected to be implemented in Pectra by early 2025. (Note: this chapter was written in September and October 2024, which is why we are using future tense.) EIP-7702 introduces a "set code transaction" under EIP-2718, enabling an EOA to delegate certain code to be executed on its behalf by authorized addresses.

EIP-7702は、2025年初頭までにPectraで実装される予定の主要なAA EIPです。（注：この章は2024年9月から10月に書かれたため、未来形を使用しています。）EIP-7702はEIP-2718の下で「セットコードトランザクション」を導入し、EOAが認可されたアドレスによって自身の代わりに実行される特定のコードをデリゲートできるようにします。

> **Note**
>
> EIP-2718 introduces a "typed transaction envelope" format for Ethereum, supporting multiple transaction types within the protocol. This standardized format allows backward-compatible transaction upgrades, enabling future improvements with new transaction types while maintaining existing structures. This will be explained in more detail in Chapter 6. This EIP also adjusts EIP-3607's restrictions, allowing transactions from EOAs flagged with a delegation designation. It enables secure delegation for EOAs, adding improved account-management capabilities to Ethereum.
>
> A question arises around how users should specify the code they intend to run in their accounts. The main options are to include the bytecode directly in the transaction or to reference a pointer to the code. The simplest pointer is the address of some code deployed on chain. Direct code specification allows EOAs to execute arbitrary code within the transaction calldata. One consideration when signing a code pointer is whether that address points to the intended code on another chain; wallet maintainers can hardcode a single EIP-7702 authorization message, ensuring cross-chain code consistency.

> **注記**
>
> EIP-2718はイーサリアムに「型付きトランザクションエンベロープ」フォーマットを導入し、プロトコル内で複数のトランザクションタイプをサポートします。この標準化されたフォーマットにより、後方互換性のあるトランザクションのアップグレードが可能になり、既存の構造を維持しながら新しいトランザクションタイプによる将来の改善が実現できます。これは第6章でより詳しく説明します。このEIPはまた、EIP-3607の制限を調整し、デリゲーション指定のフラグが付いたEOAからのトランザクションを許可します。EOAの安全なデリゲーションを可能にし、イーサリアムに改善されたアカウント管理機能を追加します。
>
> ユーザーがアカウントで実行するコードをどのように指定すべきかという疑問が生じます。主なオプションは、トランザクションにバイトコードを直接含めるか、コードへのポインターを参照するかです。最もシンプルなポインターは、オンチェーンにデプロイされたコードのアドレスです。直接コード指定により、EOAはトランザクションのcalldata内で任意のコードを実行できます。コードポインターに署名する際の1つの考慮事項は、そのアドレスが別のチェーン上の意図したコードを指しているかどうかです。ウォレットのメンテナーは単一のEIP-7702認可メッセージをハードコードすることで、クロスチェーンのコードの一貫性を確保できます。

There is an important security consideration to make. Once code is embedded in an EOA, EIP-7702 transactions may allow `msg.sender == tx.origin`, where the transaction creator is also the broadcasting address whenever the EOA code dispatches a call. Without EIP-7702, this scenario only occurs at the topmost execution layer of a transaction. Because EIP-7702 would enable transaction sponsoring, this would also be possible in other layers of execution. Consequently, this EIP breaks that invariant, affecting smart contracts that contain `require(msg.sender == tx.origin)` checks. This check serves at least three purposes:

重要なセキュリティ上の考慮事項があります。コードがEOAに組み込まれると、EIP-7702トランザクションは`msg.sender == tx.origin`を許可する可能性があります。これはEOAコードがコールを発行するたびに、トランザクションの作成者がブロードキャストアドレスでもある状態です。EIP-7702がなければ、このシナリオはトランザクションの最上位実行層でのみ発生します。EIP-7702はトランザクションスポンサーリングを可能にするため、他の実行層でもこれが可能になります。その結果、このEIPはその不変条件を破り、`require(msg.sender == tx.origin)`チェックを含むスマートコントラクトに影響を与えます。このチェックは少なくとも3つの目的を果たします：

1. Verifying that `msg.sender` is an EOA (as `tx.origin` must always be an EOA). This invariant remains unaffected by execution-layer depth; it is still possible to ensure that the `tx.origin` is the `msg.sender` if the depth of the call is 1.

1. `msg.sender`がEOAであることの検証（`tx.origin`は常にEOAでなければならないため）。この不変条件は実行層の深さに影響されません。コールの深さが1であれば、`tx.origin`が`msg.sender`であることを確認することは依然として可能です。

2. Preventing atomic sandwich attacks, such as flash loans, which rely on altering state before and after target contract execution within the same atomic transaction. This protection is compromised by this EIP. However, using `tx.origin` for this purpose is generally considered poor practice and can already be bypassed by miners selectively including transactions.

2. フラッシュローンなどのアトミックサンドイッチ攻撃の防止。これは同じアトミックトランザクション内でターゲットコントラクトの実行前後にステートを変更することに依存しています。この保護はこのEIPによって損なわれます。ただし、この目的で`tx.origin`を使用することは一般的に悪いプラクティスと見なされており、マイナーがトランザクションを選択的に含めることですでにバイパスできます。

3. Guarding against reentrancy.

3. リエントランシーに対する防御。

Examples of the first two appear in Ethereum mainnet contracts, with the first being more common (and unaffected by this EIP). However, the third case is more vulnerable under this EIP, although no instances of reentrancy protection relying on `tx.origin` were observed during the initial review by the creators of the proposal.

最初の2つの例はイーサリアムメインネットのコントラクトに存在し、1番目がより一般的です（このEIPの影響を受けません）。しかし、3番目のケースはこのEIPの下でより脆弱ですが、提案の作成者による最初のレビューでは、`tx.origin`に依存するリエントランシー保護のインスタンスは観察されませんでした。

> **Tip**
>
> Unlike prior versions of this EIP and similar proposals, the delegation designation can be revoked at any time by signing and submitting an EIP-7702 authorization targeting a new address, using the account's current nonce. Without such action, a delegation remains valid indefinitely.

> **ヒント**
>
> このEIPの以前のバージョンや類似の提案とは異なり、デリゲーション指定はアカウントの現在のナンスを使用して新しいアドレスをターゲットとするEIP-7702認可に署名して送信することで、いつでも取り消すことができます。そのようなアクションを取らない限り、デリゲーションは無期限に有効です。

There is considerable interest in adding functionality improvements to EOAs, improving usability and, in some cases, improving security. One key application is transaction sponsorship, which enables users to transact without holding ETH to cover gas fees. In traditional Ethereum transactions, gas fees are paid in ETH, which may be inconvenient for users holding only other tokens or those who are new to the ecosystem. EIP-7702 introduces a model where transaction fees can be covered by third parties, temporarily or permanently, allowing users to complete transactions without ETH. This could simplify onboarding, making Ethereum applications more accessible to new users interested in specific DApps or tokens without requiring ETH management.

EOAに機能改善を追加し、ユーザビリティや場合によってはセキュリティを向上させることへの関心は高いです。主要なアプリケーションの1つはトランザクションスポンサーシップで、ユーザーがガス代を賄うためにETHを保持せずにトランザクションを実行できるようにします。従来のイーサリアムトランザクションでは、ガス代はETHで支払われますが、これは他のトークンのみを保持しているユーザーやエコシステムの初心者にとっては不便な場合があります。EIP-7702は、トランザクション手数料を第三者が一時的または恒久的に負担できるモデルを導入し、ユーザーがETHなしでトランザクションを完了できるようにします。これによりオンボーディングが簡素化され、ETH管理を必要とせずに特定のDAppやトークンに関心のある新規ユーザーにとってイーサリアムアプリケーションがよりアクセスしやすくなります。

Traditional Ethereum accounts rely solely on a single private key, so losing it means losing access to the account and assets. EIP-7702's structure supports various recovery mechanisms, enabling users to regain access if they lose their private keys. Recovery mechanisms are especially valuable for security-focused users and for those who are new to blockchain and may find key management daunting. Potential recovery options include multisignature and social recovery, which allow selected contacts to assist in account restoration; this is a big step in Ethereum accounts' security and user-friendliness.

従来のイーサリアムアカウントは単一の秘密鍵にのみ依存しているため、紛失するとアカウントと資産へのアクセスを失うことを意味します。EIP-7702の構造はさまざまなリカバリメカニズムをサポートし、ユーザーが秘密鍵を紛失した場合にアクセスを回復できるようにします。リカバリメカニズムは、セキュリティを重視するユーザーや、ブロックチェーンの初心者で鍵管理を困難に感じるユーザーにとって特に価値があります。潜在的なリカバリオプションには、選択した連絡先がアカウントの復元を支援できるマルチシグやソーシャルリカバリが含まれます。これはイーサリアムアカウントのセキュリティとユーザーフレンドリーさにおける大きな前進です。

EIP-7702 also introduces batching and privilege deescalation. Batching allows multiple actions to be processed within a single atomic transaction, enabling users to complete complex workflows—such as ERC-20 approval followed by token spending—in one step rather than two. Privilege deescalation offers subkeys with restricted permissions, authorizing actions like spending a specific amount or interacting only with certain applications, to improve security by minimizing exposure in case of compromise.

EIP-7702はまた、バッチ処理と権限の降格も導入します。バッチ処理により、単一のアトミックトランザクション内で複数のアクションを処理でき、ERC-20の承認に続くトークンの使用など、複雑なワークフローを2ステップではなく1ステップで完了できます。権限の降格は、特定の金額の使用や特定のアプリケーションとのインタラクションのみを認可するなど、制限された権限を持つサブキーを提供し、危殆化時の露出を最小限に抑えることでセキュリティを向上させます。

This EIP also modifies the invariants that traditionally govern account balance and nonce behaviors. It breaks the expectation that the balance of an EOA account can only decrease due to transactions from that account, and that an EOA's nonce cannot increment once transaction execution begins. These changes affect the mempool design and other EIPs. However, since the accounts are statically listed in the outer transaction, transaction-propagation rules can be adjusted to prevent forwarding of conflicting transactions. It does have forward compatibility with ERC-4337 and RIP-7560. Among other benefits, it enables EOAs to masquerade as contracts compatible with ERC-4337 bundles via the existing EntryPoint mechanism.

このEIPはまた、従来アカウント残高とナンスの動作を支配してきた不変条件を変更します。EOAアカウントの残高はそのアカウントからのトランザクションによってのみ減少するという期待、およびトランザクション実行が開始されるとEOAのナンスはインクリメントできないという期待を破ります。これらの変更はメンプールの設計と他のEIPに影響します。しかし、アカウントは外部トランザクションに静的にリストされているため、トランザクション伝播ルールを調整して競合するトランザクションの転送を防止できます。ERC-4337およびRIP-7560との前方互換性を持っています。他の利点の中でも、EOAが既存のEntryPointメカニズムを通じてERC-4337バンドルと互換性のあるコントラクトとして振る舞うことを可能にします。

> **Note**
>
> A general design goal for state-transition changes is minimizing special cases in an EIP. Earlier iterations of this EIP resisted adding a special case for clearing an account's delegation designation. Generally, an account delegated to 0x0 behaves like a true EOA; however, most operations interacting with that account incur an additional cost. This extra cost may influence overall EIP adoption. For these reasons, a mechanism was included to allow users to restore their EOAs to their original state.

> **注記**
>
> 状態遷移の変更に対する一般的な設計目標は、EIP内の特殊ケースを最小限に抑えることです。このEIPの初期のイテレーションでは、アカウントのデリゲーション指定をクリアするための特殊ケースの追加に抵抗していました。一般的に、0x0にデリゲートされたアカウントは真のEOAのように動作しますが、そのアカウントとインタラクションするほとんどのオペレーションでは追加コストが発生します。この追加コストはEIP全体の採用に影響を与える可能性があります。これらの理由から、ユーザーがEOAを元の状態に復元できるメカニズムが含まれました。

This EIP involves multiple security considerations, which will be the responsibility of the implementation and should be carefully evaluated. In addition to the noted `tx.origin` issue, there are three key considerations:

このEIPには複数のセキュリティ上の考慮事項が含まれており、実装の責任であり、慎重に評価される必要があります。前述の`tx.origin`の問題に加えて、3つの主要な考慮事項があります：

- Enabling EOAs to act like smart contracts challenges transaction propagation. Traditionally, EOAs could only send value via transactions. With this EIP, an EOA's delegated code can be invoked by anyone at any time in a transaction, preventing static balance validation by nodes; it essentially makes it harder for nodes to validate the balance of an address.

- EOAがスマートコントラクトのように動作できるようにすることは、トランザクション伝播に課題をもたらします。従来、EOAはトランザクションを通じてのみ値を送信できました。このEIPにより、EOAのデリゲートされたコードはトランザクション内で誰でもいつでも呼び出すことができ、ノードによる静的な残高検証を妨げます。これは本質的に、ノードがアドレスの残高を検証することをより困難にします。

- Smart contract wallet developers must consider the implications of setting code in an account without execution. Normally, contracts are deployed with initcode, initializing storage slots deterministically. This EIP omits initcode execution for delegation, so developers must verify initial calldata to prevent an observer from front-running setup with an account they control.

- スマートコントラクトウォレットの開発者は、実行なしでアカウントにコードを設定することの影響を考慮する必要があります。通常、コントラクトはinitcodeでデプロイされ、ストレージスロットを決定論的に初期化します。このEIPはデリゲーションのためのinitcode実行を省略するため、開発者は観察者が自分の制御するアカウントでセットアップをフロントランニングすることを防ぐために、初期calldataを検証する必要があります。

- Replay protection (e.g., nonce handling) should be implemented by the delegate and signed. Without this, a malicious actor could reuse a signature, gaining near-complete control over the signer's EOA.

- リプレイ保護（例：ナンスの処理）はデリゲートによって実装され、署名される必要があります。これがなければ、悪意のある行為者が署名を再利用し、署名者のEOAに対するほぼ完全な制御を得る可能性があります。

#### The future of account abstraction
#### アカウントアブストラクションの将来

AA on Ethereum is a complex but promising idea, with many possible paths forward. Each proposal offers a different way to make user interactions simpler and more secure. Some improve on previous proposals, such as EIP-5003 building on EIP-3074, while others, such as EIP-5806, stand alone or even lack backward compatibility. This variety reflects a search for the best solution, with the final direction likely shaped by which options users find easiest and most effective. Although the exact future is unclear, AA holds real promise for improving the experience of using Ethereum.

イーサリアムにおけるAAは複雑ですが有望なアイデアであり、前進するための多くの道筋があります。各提案はユーザーのインタラクションをよりシンプルで安全にするための異なる方法を提供しています。EIP-3074の上に構築されたEIP-5003のように以前の提案を改善するものもあれば、EIP-5806のように単独で成立するものや後方互換性を欠くものもあります。この多様性は最適なソリューションの探求を反映しており、最終的な方向性はユーザーが最も簡単で効果的だと感じるオプションによって形作られる可能性が高いです。正確な将来は不透明ですが、AAはイーサリアムの利用体験を改善する真の可能性を秘めています。

### Social Recovery
### ソーシャルリカバリ

The primary EIP related to social recovery is EIP-2429. Titled "Secret Multisig Recovery," EIP-2429 introduces a mechanism that allows users to regain access to their wallets by assigning trusted individuals or entities as "guardians." In case a user loses their private key, they can use these guardians to help recover control of the wallet. The guardians are involved only during the recovery process, limiting their power, as shown in Figure 5-10.

ソーシャルリカバリに関連する主要なEIPはEIP-2429です。「Secret Multisig Recovery」というタイトルのEIP-2429は、信頼できる個人またはエンティティを「ガーディアン」として指定することで、ユーザーがウォレットへのアクセスを回復できるメカニズムを導入します。ユーザーが秘密鍵を紛失した場合、これらのガーディアンを利用してウォレットの制御を回復できます。図5-10に示すように、ガーディアンはリカバリプロセス中のみ関与し、その権限は限定されています。

![Social recovery flow](images/ch5/maet_0510.png)

Figure 5-10. Social recovery flow

図5-10. ソーシャルリカバリのフロー

> **Note**
>
> Vitalik Buterin released an article in 2021 that said, and we are quoting, "This gets us to my preferred method for securing a wallet: social recovery." We do not know if the situation has changed, but it still might be the case that social recovery is Buterin's preferred method.

> **注記**
>
> Vitalik Buterinは2021年に記事を公開し、引用すると「これが私のウォレットを保護するための好ましい方法、つまりソーシャルリカバリにたどり着く」と述べています。状況が変わったかどうかは不明ですが、ソーシャルリカバリが依然としてButerinの好ましい方法である可能性があります。

For normal use, a social recovery wallet functions like a regular one, allowing the user to sign transactions with their signing key. If the key is lost, social recovery activates, enabling the user to contact guardians, who sign a transaction to update the wallet's signing key. Guardians can be trusted individuals, devices, or institutions. Guardians can remain anonymous, and to prevent attacks, their identities aren't stored on chain. In case of the user's death, guardians can coordinate to recover the user's funds.

通常の使用では、ソーシャルリカバリウォレットは通常のウォレットと同様に機能し、ユーザーは署名鍵でトランザクションに署名できます。鍵が紛失した場合、ソーシャルリカバリが有効になり、ユーザーはガーディアンに連絡でき、ガーディアンはウォレットの署名鍵を更新するトランザクションに署名します。ガーディアンは信頼できる個人、デバイス、または機関です。ガーディアンは匿名のままでいることができ、攻撃を防ぐために、その身元はオンチェーンに保存されません。ユーザーの死亡時には、ガーディアンが連携してユーザーの資金をリカバリできます。

### ENS

The Ethereum Name Service is like a Web3 version of traditional domain names, but instead of linking to websites, it connects human-readable names to Ethereum addresses. This makes dealing with long, complex blockchain addresses much easier. For instance, rather than having to send cryptocurrency to an address like `0xd8dA6BF...`, you can simply send it to something like `vitalik.eth`. This simplifies transactions and makes the whole process far less intimidating, especially for newcomers to crypto.

Ethereum Name Service（ENS）は従来のドメイン名のWeb3バージョンのようなものですが、ウェブサイトにリンクする代わりに、人間が読める名前をイーサリアムアドレスに接続します。これにより、長く複雑なブロックチェーンアドレスの扱いがはるかに簡単になります。例えば、`0xd8dA6BF...`のようなアドレスに暗号通貨を送信する代わりに、`vitalik.eth`のようなものに送信するだけで済みます。これによりトランザクションが簡素化され、特に暗号通貨の初心者にとってプロセス全体がはるかに取り組みやすくなります。

If you compare ENS to the Web2 world, it's similar to how DNS works. DNS takes IP addresses (which are hard to remember) and connects them to URLs like `google.com`, so you don't have to remember a string of numbers to visit a website. However, there's a key difference between ENS and DNS: ENS is decentralized. No central authority controls your `.eth` name once you own it. In Web2, domain names are managed by registrars and can be censored, suspended, or restricted. In ENS, you control your name entirely through your Ethereum wallet, meaning your `.eth` name is as secure as the wallet that holds it.

ENSをWeb2の世界と比較すると、DNSの仕組みに似ています。DNSはIPアドレス（覚えにくい）を`google.com`のようなURLに接続するため、ウェブサイトを訪れるのに数字の文字列を覚える必要がありません。しかし、ENSとDNSの間には重要な違いがあります。ENSは分散型です。一度`.eth`名を所有すれば、中央の権限がそれを制御することはありません。Web2では、ドメイン名はレジストラによって管理され、検閲、停止、制限される可能性があります。ENSでは、イーサリアムウォレットを通じて名前を完全に制御できるため、`.eth`名はそれを保持するウォレットと同じくらい安全です。

When you're sending or receiving crypto, using a name like `andreas.eth` instead of a long, complex Ethereum address makes everything smoother and safer. It reduces the chance of making a mistake when entering an address, which can otherwise be a big risk in a transaction.

暗号通貨を送受信するとき、長く複雑なイーサリアムアドレスの代わりに`andreas.eth`のような名前を使用すると、すべてがよりスムーズで安全になります。アドレスの入力時にミスをする可能性が減少します。アドレスの入力ミスは、トランザクションにおいて大きなリスクとなりえます。

Another cool aspect of ENS is that it provides a sense of digital identity. Just like owning a domain name for your website, having a unique `.eth` name can serve as your public identity on the blockchain.

ENSのもう1つの興味深い側面は、デジタルアイデンティティの感覚を提供することです。ウェブサイトのドメイン名を所有するのと同じように、ユニークな`.eth`名はブロックチェーン上のパブリックアイデンティティとして機能できます。

## Conclusion
## まとめ

Wallets are the foundation of any user-facing blockchain application. They enable users to manage collections of keys and addresses. Wallets also allow users to demonstrate their ownership of ether and authorize transactions by applying digital signatures, as we will see in Chapter 6.

ウォレットは、ユーザー向けのあらゆるブロックチェーンアプリケーションの基盤です。ウォレットにより、ユーザーは鍵とアドレスのコレクションを管理できます。また、ウォレットはユーザーがEtherの所有権を証明し、第6章で見るようにデジタル署名を適用してトランザクションを承認することも可能にします。
