# 第8章　スマートコントラクトとVyper

　Vyperは、EVM向けに設計された確立されたコントラクト指向プログラミング言語であり、開発者がわかりやすいコードを書けるようにすることで、優れた監査性の提供を目指しています。実際、Vyperの原則の1つは、誤解を招くようなコードを開発者が事実上書けないようにすることです。

　本章では、スマートコントラクトに関するよくある問題を検討し、Vyperコントラクト プログラミング言語を紹介したうえで、Solidityと比較してその違いを説明します。

## 脆弱性とVyper

　2023年だけで、イーサリアム エコシステムにおけるスマートコントラクトの脆弱性により、約20億ドルが盗まれました。スマートコントラクトの脆弱性は、コードに起因します。こうした脆弱性が意図的なものとは考えにくいですが、いずれにせよ、望ましくないスマートコントラクトのコードがイーサリアム ユーザの予期しない資金喪失を招いていることは明らかであり、理想的な状況ではありません。Vyperは安全なコードをより簡単に書けるよう、また誤解を招くコードや脆弱なコードを誤って書いてしまうことがより難しくなるよう設計されています。

## Solidityとの比較

　Vyperが安全でないコードを書きにくくする方法の1つは、Solidityのいくつかの機能を意図的に除外することです。この設計上の選択は、セキュリティ最優先の原則と、Pythonの明確さやシンプルさから着想を得たVyperのルーツを反映しています。Vyperでのスマートコントラクト開発を検討する場合、Vyperにどの機能がなく、なぜないのかを理解することが重要です。この節では除外された機能を詳しく調べ、その理由を見ていきます。

　機能セットを削減して曖昧さを減らす一方で、Vyperは開発者や監査者の実際のニーズに応えるよう進化してきました。たとえば、コントラクトを単一ファイルに収めるという当初の方針は監査性の最大化に役立ちましたが、プロトコルが大規模かつ複雑になるにつれてボトルネックとなりました。この問題に対処するため、現代のVyperでは洗練されたモジュールシステムが導入されています。状態へのアクセスやコード再利用に対する厳密な制御を維持しつつ、コントラクトを複数のファイルに分割できるようになりました。このモジュールシステムは従来の継承ではなくコンポジションの原則に従い、構造と可読性のバランスをうまく取っています。DeFiプロトコルやステーキングシステムなど高い信頼性が求められる分野では、コードの明確さと監査のしやすさからVyperの採用が広がっています。

### 修飾子

　7章で見たように、Solidityでは修飾子を用いた関数を書くことができます。たとえば、次に示す`changeOwner`関数は、`onlyBy`と呼ばれる修飾子のコードを処理の一部として実行します。

```solidity
function changeOwner(address _newOwner)
 public
 onlyBy(owner)
{
 owner = _newOwner;
}
```

　この修飾子は所有権に関するルールを強制します。以下に示すとおり、`changeOwner`関数に代わって事前チェックを実行する仕組みです。

```solidity
modifier onlyBy(address _account)
{
 require(msg.sender == _account);
 _;
}
```

　しかし修飾子は、ここに示したようなチェックを実行するためだけに存在するわけではありません。実際、修飾子は呼び出し元の関数の実行中に、スマートコントラクトの環境を大きく変化させることができます。端的にいえば、修飾子の影響範囲は*広範*です。

　別のSolidityの例を見てみましょう。

```solidity
enum Stages {
 SafeStage,
 DangerStage,
 FinalStage
}
uint public creationTime = block.timestamp;
Stages public stage = Stages.SafeStage;
function nextStage() internal {
 stage = Stages(uint256(stage) + 1);
}
modifier stageTimeConfirmation() {
 if (stage == Stages.SafeStage &&
 block.timestamp >= creationTime + 10 days)
 nextStage();
 _;
}
function a()
 public
 stageTimeConfirmation
 // More code goes here
{
}
```

　開発者は自身のコードが呼び出す他のコードを常にチェックすべきです。ただし、時間的制約がある場合や疲労で集中力が低下している場合など、特定の状況下ではコードのある1行を見落とすこともありえます。関数呼び出しの階層構造を頭の中で追いかけながら、スマートコントラクトの変数の状態を記憶しつつ巨大なファイル内を探索しなければならない場合は、なおさらです。

　先に挙げた例をもう少し詳しく見てみましょう。開発者が`a`という公開関数を書いているとします。この開発者はコントラクトに触れるのが初めてで、他の誰かが書いた修飾子を利用しようとしています。一見すると`stageTimeConfirmation`修飾子は、呼び出し元の関数に関連してコントラクトの経過時間をチェックしているだけのように見えます。しかし実際には、この修飾子は`nextStage`というもう1つの関数を呼び出しており、開発者はそれに気づか*ない*かもしれません。この単純化されたシナリオでは、公開関数`a`を呼び出すだけでスマートコントラクトの`stage`変数が`SafeStage`から`DangerStage`に変わります。

　Vyperでは修飾子が完全に廃止されています。Vyperの推奨は次のとおりです。修飾子でアサーションのみを行いたい場合は、インラインのチェックとアサートを関数の一部として使用します。スマートコントラクトの状態を変更する場合も同様に、変更を関数内に明示します。こうすれば、読み手は関数の動作を理解するために修飾子のコードを頭の中で（あるいは手動で）「包む」必要がなくなり、可監査性と可読性が向上します。

### クラスの継承

　プログラマーは継承を使って、既存のソフトウェアライブラリからあらかじめ用意された機能や性質、振る舞いを獲得し、すでに書かれたコードを活用できます。継承は強力で、コードの再利用を促進します。Solidityはオブジェクト指向プログラミングの重要な機能であるポリモーフィズム（多態性）と多重継承をサポートしていますが、Vyperはどちらもサポートしていません。Vyperの考え方では、継承を実装するにはコードの作成者や監査者が複数のファイル間を行き来して、プログラムの動作を理解する必要があります。また、多重継承はコードを理解不可能なほど複雑にする可能性があるとVyperは考えています。これは[Solidityのドキュメント](https://oreil.ly/bkGwS)でも暗に認められており、多重継承がどのように問題になりうるかの例が示されています。

### インラインアセンブリ

　インラインアセンブリを用いると、開発者はEVMへの低レベルなアクセスが可能になり、SolidityのプログラムからEVMの命令に直接アクセスして操作を実行できます。たとえば、次のアセンブリコードはメモリ番地`0x80`に3を加算します。

```
3 0x80 mload add 0x80 mstore
```

　インラインアセンブリを使用すると、変数名を検索してその変数が読み書きされるすべての箇所を特定できなくなります。Vyperは追加的な機能と引き換えに可読性を犠牲にするのは代償が大きすぎると判断し、インラインアセンブリをサポートしていません。

### 関数のオーバーロード

　関数のオーバーロードを用いると、開発者は同じ名前の関数を複数書くことができます。どの関数が使われるかは、その時々で渡される引数の型に依存します。例として、次の2つの関数を見てみましょう。

```solidity
function f(uint256 _in) public pure returns (uint256 out) {
 out = 1;
}
function f(uint256 _in, bytes32 _key) public pure returns (uint256 out) {
 out = 2;
}
```

　最初の関数（名称は`f`）はuint256型の入力引数を1つ受け取ります。2つ目の関数（こちらの名称も`f`）は2つの引数を受け取り、1つはuint256型、もう1つはbytes32型です。異なる引数を取る同名の関数が複数定義されている状況は混乱を招くため、Vyperは関数のオーバーロードをサポートしていません。

### 変数の型キャスト

　Vyperは型変換に対してSolidityとは大きく異なるアプローチを取っており、利便性よりも明示的で安全な型の扱いを優先しています。すべての型変換は組み込みの`convert()`関数で明示的に行う必要があり、データ型がいつどのように変更されるかを開発者が常に把握できます。

　型変換は、情報が失われる可能性のあるものと失われないものの2つに分けられます。Vyperの`convert()`関数はどちらも扱えますが、予期しない動作を防ぐために常に明示的な境界チェックを行います。たとえば、大きな整数型から小さな整数型に変換する場合、値が変換先の型の範囲に収まらなければトランザクションをリバートします。

　Vyperにおける型変換の構文はシンプルです。

```
# 整数型間の変換
small_value: uint8 = 42
large_value: uint256 = convert(small_value, uint256)  # 安全なアップキャスト
back_to_small: uint8 = convert(large_value, uint8)   # 境界チェック付きダウンキャスト
```

　この明示的なアプローチにより、型変換の場面ではVyperのコードはSolidityよりも冗長になりますが、はるかに安全です。すべての変換が意図的かつ明示的でなければならないため、値の切り捨てや予期しないオーバーフローが誤って発生する余地はありません。`convert()`関数は、変換でデータが失われる場合や入力値が変換先の型の有効範囲外である場合にトランザクションをリバートします。

## デコレータ

　関数の開始部に、次に挙げるデコレータを使うことができます。

**@internal**

`@internal`デコレータは、関数をコントラクトの外部からアクセス不可にする。これはデフォルトの関数可視性であるため、省略可能である。

**@external**

`@external`デコレータは、関数を外部から可視かつ実行可能にする。たとえば、イーサリアムウォレットもコントラクトを参照するときにこれらの関数を表示する。

**@view**

`@view`デコレータを付けた関数は状態変数を変更できない。実際、このデコレータが付いた関数が状態変数を更新しようとすると、コンパイラはプログラム全体を（適切なエラーで）拒否する。

**@pure**

`@pure`デコレータを付けた関数は、ブロックチェーンの状態を読み取ったり、pureでないメソッドや他のコントラクトを呼び出したりできない。

**@payable**

`@payable`デコレータを持つ関数のみがバリューを転送できる。

**@deploy**

`@deploy`デコレータは、コントラクトのコンストラクタ関数を示す。この関数はコントラクトがブロックチェーンにデプロイされるときに1度だけ実行され、通常は初期状態変数や設定のセットアップに用いられる。Vyperでは`__init__()`関数のみに`@deploy`を付けることができ、コントラクトにコンストラクタロジックを含める場合はこのデコレータが必須である。

**@raw_return**

`@raw_return`デコレータを付けた関数は、ABIエンコーディングを適用せずに生のバイト列を返す。別のコントラクト呼び出しの出力を追加のエンコーディングなしにそのまま転送する必要があるプロキシコントラクトやヘルパーコントラクトで特に有用である。ただし重要な制限があり、`@external`関数にのみ使用でき、インターフェース定義では使用できない。他のコントラクトからこの関数を呼び出す場合は、戻り値がABIエンコードされていない可能性があるため、インターフェース呼び出しではなく`raw_call`を使用する。

**@nonreentrant**

`@nonreentrant`デコレータは関数にロックをかけ、対象の関数が実行完了するまで再度呼び出せないようにする。外部コントラクトが保護された関数にコールバックして予期しない動作や悪用を引き起こすリエントランシー攻撃を防ぐために使用される。Vyperはデフォルトでリエントランシー防止のプラグマもサポートしており、明示的にオーバーライドしない限りすべての外部関数がリエントラント不可となる。たとえば、コントラクトAがこのデコレータを使用してコントラクトBに外部呼び出しを行った場合、コントラクトBがコントラクトAの保護された関数にコールバックしようとするとトランザクションはリバートされる。

> **注記**
>
> Vyperバージョン0.2.15、0.2.16、0.3.0のnonreentrant機能には、2023年半ばに発見されCurveプロトコルへの攻撃に悪用された重大なバグが含まれていた。リエントランシーの脆弱性については9章で詳しく取り上げる。


　Vyperはデコレータのロジックを明示的に実装しています。たとえば`@payable`と`@view`の両方を持つ関数があると、Vyperのコンパイルは失敗します。バリューを転送する関数は定義上、状態を更新するため`@view`にはなりえません。Vyperの関数には`@external`か`@internal`のどちらかを付ける必要があります（両方は不可です）。

## 関数と変数の順序

　Vyperのスコープと宣言はC99のスコープ規則に従っており、想像以上の柔軟性があります。Vyperのコントラクトは依然として単一ファイル内に収める必要がありますが（モジュールシステムを使用しない場合）、以前のバージョンにあった厳密な順序制約は、モジュールスコープの宣言では緩和されています。

　モジュールスコープ（関数本体の外側）で宣言された変数や関数は、正式な宣言よりも前であってもコントラクト全体から参照できます。多くの現代的なプログラミング言語における前方宣言と同様に、状態変数の参照や関数の呼び出しを、ファイル内での記述位置より前に行えます。

　現代のVyperにおけるスコープの動作を示す例を見てみましょう。

```
# この関数は下で宣言される状態変数を参照できる
@external
def get_stored_value() -> uint256:
    return self.stored_data  # 後で宣言される変数を参照
# この関数は上の関数を呼び出すことができる
@external
def check_if_positive() -> bool:
    return self.get_stored_value() > 0
# 状態変数の宣言 - 上の関数からアクセス可能
stored_data: public(uint256)
```

　ただし関数スコープ内では、Vyperは依然として厳密な順序規則を維持しています。ローカル変数は使用前に宣言する必要があり、定数やイミュータブル変数などモジュールレベルの宣言名をローカル変数でシャドーイングすることはできません。このアプローチはPythonの柔軟性と、状態変数や関数の関係が明確に見えることがセキュリティ監査上重要であるスマートコントラクト開発のニーズとのバランスを取っています。

## コンパイル

　Vyperを試す最も簡単な方法は、[Remixオンラインコンパイラ](https://remix.ethereum.org)を使うことです。Webブラウザだけを用いてスマートコントラクトを作成し、コンパイルできます（プラグインマネージャでvyper-remixプラグインを有効化する必要があります）。

> **注記**
>
> Vyperには[組み込みの共通インターフェース](https://oreil.ly/GazPW)（ERC-20やERC-721など）が付属しており、これらのコントラクトとのやりとりをすぐに利用できる。Vyperにおけるコントラクトはグローバル変数として宣言する必要がある。ERC-20変数の宣言例は次のとおりである。
> `from vyper.interfaces import ERC20` `token: ERC20`


　コマンドラインからコントラクトをコンパイルすることもできます。Vyperのコントラクトはそれぞれ *.vy* 拡張子のファイルに保存されます。Vyperをインストールすれば、次のコマンドでコントラクトをコンパイルできます。

```bash
vyper ~/hello_world.vy
```


　コンパイラは豊富な出力オプションを備えています。人間が読みやすいJSON形式のABI記述を取得するには、次のコマンドを使用します。

```bash
vyper -f abi ~/hello_world.vy
```


　開発やテストでは、バイトコード、オペコード、インターフェースファイルなどの追加出力が必要になることもあるでしょう。コンパイラは多数の出力フォーマットをサポートしています。

```bash
vyper -f abi,bytecode,interface,source_map ~/hello_world.vy
```


　現代のVyperには高度な最適化モードも含まれています。`--optimize gas`（デフォルト）でガス効率の最適化、`--optimize codesize`でコントラクトサイズの最小化が可能です。新しい実験的なVenom IRパイプラインは`--experimental-codegen`で有効化でき、さらに優れた最適化を実現します。


　Remixやコマンドラインコンパイラは学習や実験に最適ですが、大規模なプロジェクトでは包括的な開発フレームワークが必要になります。[ApeWorx](https://oreil.ly/AJRSa)（旧Ape）は自動テストやデプロイスクリプティング、さまざまなネットワークとの統合といった機能を備え、Vyperを手厚くサポートしています。[Foundry](https://oreil.ly/CWIKj)は主にSolidity向けですがVyperの開発もサポートしており、強力なテストやシミュレーション機能を提供しています。これらのフレームワークは、複雑なアプリケーションを構築するプロフェッショナルなスマートコントラクト開発者に必要な成熟した開発環境を提供します。

## コンパイラレベルでのオーバーフローエラーに対する保護

　ソフトウェアにおけるオーバーフローエラーは、実際の価値を扱う場合に破滅的な結果をもたらすことがあります。たとえば、[2018年4月中旬のあるトランザクション](https://oreil.ly/zOy06)は、57,896,044,618,658,100,000,000,000,000,000,000,000,000,000,000,000,000,000,000を超えるBECトークンの不正な移転を示しています。このトランザクションは、Beauty ChainのERC-20トークンコントラクト（*BecToken.sol*）における整数オーバーフローが原因でした。

　Vyperのコア機能の1つは、スマートコントラクト開発を歴史的に悩ませてきたオーバーフローエラーのリスクを軽減する組み込みのオーバーフロー保護です。Vyperのオーバーフロー保護は包括的で、整数演算の例外ケースを処理するSafeMath相当の保護を含んでいます。加算や減算、乗算、除算などの操作はデフォルトで安全であり、オーバーフローやアンダーフローが発生すると例外がスローされます。加えて、定数リテラルの読み込みや関数への値の受け渡し、変数への代入のたびにクランプ（値の範囲チェック）を使って値の制限を強制します。

　Solidityの最近のバージョン（0.8.0以降）でも、Vyperが当初から提供してきたものと同様のネイティブなオーバーフローチェックがコンパイラレベルで統合されています。これにより現代のSolidityでは算術演算にオーバーフローチェックが自動的に含まれ、SafeMathのような追加ライブラリなしでオーバーフローエラーのリスクが大幅に低減されました。この変更でSolidityはVyperのセキュリティ最優先のアプローチに近づきましたが、Vyperの実装はクランプ操作や言語全体にわたるより一貫した境界チェックを含め、依然としてより包括的です。根本的な違いは思想にあります。Vyperはオーバーフロー保護をコア原則として最初から設計されたのに対し、Solidityは歴史的な脆弱性への対処として後から追加しました。このアプローチの違いは、安全でないコードをデフォルトで書きにくくするというVyperの設計思想を反映しています。

## Reading and Writing Data

## データの読み書き


Even though it is costly to store, read, and modify data, these storage operations are a necessary component of most smart contracts. Smart contracts can write data to two places:

　データの保存、読み込み、修正にはコストがかかりますが、これらのストレージ操作はほとんどのスマートコントラクトに必要な要素です。スマートコントラクトは、2つの場所にデータを書き込むことができます。

**Global state**

**グローバル状態**


The state variables in a given smart contract are stored in Ethereum's global state trie; a smart contract can only store, read, and modify data in relation to that particular contract's address (i.e., smart contracts cannot directly read or write to other smart contracts).

特定のスマートコントラクトの状態変数は、イーサリアムのグローバルな状態トライ木に記録されている。スマートコントラクトは、その特定のコントラクトアドレスに関連するデータのみを保存、読み取り、修正できる（つまり、スマートコントラクトは他のスマートコントラクトに対して直接読み書きできない）。

**Logs**

**ログ**


A smart contract can write to Ethereum's chain data through log events. In Vyper, the syntax for declaring and using events is clean and straightforward, aligning with Vyper's focus on code clarity.

スマートコントラクトは、ログイベントを通じてイーサリアムのチェーンデータに書き込むことができる。Vyperでは、イベントの宣言と使用の構文がクリーンかつわかりやすく、コードの明確さを重視するVyperの方針に沿っている。


Event declarations in Vyper look similar to struct declarations. For example, the declaration of an event called `MyLog` is written as:

　Vyperのイベント宣言は構造体の宣言に似ています。たとえば、`MyLog`というイベントの宣言は次のように記述します。

```
event MyLog:
    arg1: indexed(address)
    arg2: uint256
    message: indexed(bytes[100])
```


You can have up to four indexed arguments (these become searchable topics) and any number of nonindexed arguments that become part of the event data. Indexed arguments are useful for filtering and searching events, while nonindexed arguments can contain larger amounts of data.

　インデックス付き引数は最大4つまで持つことができ（これらは検索可能なトピックとなります）、インデックスなしの引数はイベントデータの一部となり、個数に制限はありません。インデックス付き引数はイベントのフィルタリングや検索に有用であり、インデックスなしの引数はより大量のデータを含むことができます。


The execution of the log event uses the `log` statement with straightforward syntax:

　ログイベントの実行には、`log`文をわかりやすい構文で使用します。

```
log MyLog(msg.sender, 42, b"Hello, Vyper!")
```


You can also create events with no arguments using the `pass` statement:

　`pass`文を使って引数なしのイベントを作成することもできます。

```
event SimpleEvent: pass
# コード内で使用する場合：
log SimpleEvent()
```


While smart contracts can write to Ethereum's chain data through log events, they are unable to read the on-chain log events they've created. However, one of the advantages of writing to Ethereum's chain data via log events is that logs can be discovered and read on the public chain by light clients. For example, the `logsBloom` value in a published block can indicate whether or not a log event is present. Once the existence of log events has been established, the log data can be obtained from a given transaction receipt.

　スマートコントラクトはログイベントを通じてイーサリアムのチェーンデータに書き込むことができますが、自身が作成したオンチェーンのログイベントを読み込むことはできません。それにもかかわらず、ログイベントを通じてイーサリアムのチェーンデータに書き込むことの利点の1つは、軽量クライアントによってパブリックチェーン上でログが検出され、読み込まれることです。たとえば、公開されたブロックの`logsBloom`の値は、ログイベントが存在するかどうかを示しています。ログイベントの存在が確認されれば、与えられたトランザクションレシートからログデータを取得できます。

## Conclusion

## まとめ


Vyper is a powerful and fascinating contract-oriented programming language. Its design is biased toward "correctness," prioritizing security and simplicity. This approach may allow programmers to write better smart contracts and avoid certain pitfalls that can cause serious vulnerabilities to arise.

　Vyperは、強力で興味深いコントラクト指向のプログラミング言語です。その設計はセキュリティとシンプルさを優先し、「正確さ」に偏っています。このアプローチにより、プログラマーはより良いスマートコントラクトを作成し、深刻な脆弱性を引き起こす落とし穴を避けることができるでしょう。


However, it's important to recognize that everything has trade-offs. While Vyper's stringent design principles enhance security and code clarity, they also limit some of the flexibility that developers may find in other languages. Additionally, Vyper is not as widely used or as developed as Solidity, which means fewer resources, libraries, and tools are available for developers. This can pose challenges for those who are looking to find community support, prebuilt solutions, and comprehensive documentation.

　しかし、すべてにはトレードオフがあることを認識することが重要です。Vyperの厳格な設計原則はセキュリティとコードの明確さを向上させますが、他の言語で利用できる柔軟性の一部を制限することにもなります。さらに、VyperはSolidityほど広く使われておらず、開発も進んでいないため、開発者が利用できるリソース、ライブラリ、ツールが少ないのが現状です。コミュニティのサポート、既製のソリューション、包括的なドキュメントを求める開発者にとっては、課題となりえます。


Next, we will look at smart contract security in more detail. Some of the nuances of Vyper design may become more apparent once you read about all the possible security problems that can arise in smart contracts.

　次章では、スマートコントラクトのセキュリティをより詳細に検討します。スマートコントラクトで発生しうるあらゆるセキュリティ上の問題について読めば、Vyperの設計上のいくつかの重要なポイントがより明確になるでしょう。
