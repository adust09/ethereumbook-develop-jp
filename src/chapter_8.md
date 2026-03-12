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

### Class Inheritance

### クラスの継承


Inheritance allows programmers to harness the power of prewritten code by acquiring preexisting functionality, properties, and behaviors from existing software libraries. Inheritance is powerful and promotes the reuse of code. Solidity supports multiple inheritance as well as polymorphism, but while these are key features of object-oriented programming, Vyper does not support them. Vyper maintains that the implementation of inheritance requires coders and auditors to jump between multiple files in order to understand what the program is doing. Vyper also takes the view that multiple inheritance can make code too complicated to understand—a view tacitly admitted by the [Solidity documentation](https://oreil.ly/bkGwS), which gives an example of how multiple inheritance can be problematic.

　プログラマーは継承を使って、既存のソフトウェアライブラリからあらかじめ用意された機能、性質、振る舞いを獲得し、すでに書かれたコードを活用できるようになります。継承は強力で、コードの再利用を促進します。Solidityはオブジェクト指向プログラミングの重要な機能であるポリモーフィズム（多態性）と多重継承をサポートしていますが、Vyperはどちらもサポートしていません。Vyperの考え方では、継承を実装するにはコードの作成者や監査者が複数のファイル間を行き来して、プログラムが何を行っているかを理解する必要があります。さらに、多重継承はコードを理解不可能なほど複雑にする可能性があるとVyperは考えています。これは[Solidityのドキュメント](https://oreil.ly/bkGwS)でも暗黙のうちに認められており、多重継承がどのように問題になりうるかの例が示されています。

### Inline Assembly

### インラインアセンブリ


Inline assembly gives developers low-level access to the EVM, allowing Solidity programs to perform operations by directly accessing EVM instructions. For example, the following assembly code adds 3 to memory location `0x80`:

　インラインアセンブリを用いると、開発者はEVMへの低レベルなアクセスが可能になり、SolidityのプログラムからEVMの命令に直接アクセスして操作を実行できます。たとえば、次のアセンブリコードはメモリ番地`0x80`に3を加算します。

```
3 0x80 mload add 0x80 mstore
```


This would prevent the ability to search for a variable name to locate all occurrences where the variable is read or modified. Vyper considers the loss of readability to be too high a price to pay for the extra power and thus does not support inline assembly.

　インラインアセンブリを使用すると、変数名を検索してその変数が読み書きされるすべての箇所を特定することができなくなります。Vyperは可読性の低下が追加的な機能に対して払う代償として大きすぎると判断しており、インラインアセンブリをサポートしていません。

### Function Overloading

### 関数のオーバーロード


Function overloading allows developers to write multiple functions of the same name. Which function is used on a given occasion depends on the types of the arguments supplied. Take the following two functions, for example:

　関数のオーバーロードを用いると、開発者は同じ名前の関数を複数書くことができます。どの関数が使われるかは、その時々で渡される引数の型に依存します。例として、次の2つの関数を見てみましょう。

```solidity
function f(uint256 _in) public pure returns (uint256 out) {
 out = 1;
}
function f(uint256 _in, bytes32 _key) public pure returns (uint256 out) {
 out = 2;
}
```


The first function (named `f`) accepts an input argument of type `uint256`; the second function (also named `f`) accepts two arguments, one of type `uint256` and one of type `bytes32`. Having multiple function definitions with the same name taking different arguments can be confusing, so Vyper does not support function overloading.

　最初の関数（名称は`f`）はuint256型の入力引数を1つ受け取ります。2つ目の関数（こちらの名称も`f`）は2つの引数を受け取り、1つはuint256型、もう1つはbytes32型です。異なる引数を取る同名の関数が複数定義されている状況は混乱を招くため、Vyperは関数のオーバーロードをサポートしていません。

### Variable Typecasting

### 変数の型キャスト


Vyper takes a very different approach to type conversion compared to Solidity, prioritizing explicit and safe type handling over convenience. The language requires all type conversions to be made explicitly using the built-in `convert()` function, which ensures that developers are always aware of when and how data types are being modified.

　Vyperは型変換に対してSolidityとは大きく異なるアプローチを取っており、利便性よりも明示的で安全な型の扱いを優先しています。Vyperではすべての型変換を組み込みの`convert()`関数を使って明示的に行う必要があり、データ型がいつどのように変更されるかを開発者が常に意識できるようになっています。


We can think of type conversions in two categories: those that might lose information and those that don't. Vyper's `convert()` function handles both cases, but always with explicit bounds checking to prevent unexpected behavior. For example, when converting from a larger integer type to a smaller one, Vyper will revert the transaction if the value doesn't fit within the bounds of the target type.

　型変換は、情報が失われる可能性のあるものと失われないものの2つのカテゴリに分けて考えることができます。Vyperの`convert()`関数はどちらの場合も扱えますが、予期しない動作を防ぐために常に明示的な境界チェックを行います。たとえば、大きな整数型から小さな整数型に変換する場合、値が変換先の型の範囲に収まらなければ、Vyperはトランザクションをリバートします。


The syntax for type conversion in Vyper is straightforward:

　Vyperにおける型変換の構文はシンプルです。

```
# 整数型間の変換
small_value: uint8 = 42
large_value: uint256 = convert(small_value, uint256)  # 安全なアップキャスト
back_to_small: uint8 = convert(large_value, uint8)   # 境界チェック付きダウンキャスト
```


This explicit approach means that while Vyper code may be more verbose than Solidity when dealing with type conversions, it's also much safer. There's no possibility of accidentally truncating values or having unexpected overflow behavior because every conversion must be intentional and explicit. The `convert()` function will revert the transaction if the conversion would result in data loss or if the input value is outside the valid range for the target type.

　この明示的なアプローチにより、型変換の場面ではVyperのコードはSolidityよりも冗長になりますが、はるかに安全です。すべての変換が意図的かつ明示的でなければならないため、値の切り捨てや予期しないオーバーフロー動作が誤って発生する余地はありません。`convert()`関数は、変換によってデータが失われる場合や、入力値が変換先の型の有効範囲外である場合にトランザクションをリバートします。

## Decorators

## デコレータ


The following decorators may be used at the start of each function:

　関数の開始部に、次に挙げるデコレータを使うことができます。

**@internal**


The `@internal` decorator makes the function inaccessible from outside the contract. This is the default function visibility, and as such, it is optional.

`@internal`デコレータは、関数をコントラクトの外側からアクセス不可能にする。これはデフォルトの関数可視性であるため、省略可能である。

**@external**


The `@external` decorator makes the function both visible and executable publicly. For example, even the Ethereum wallet will display such functions when viewing the contract.

`@external`デコレータは、関数を外部から見えるようにし、公開的に実行可能にする。たとえば、イーサリアムウォレットもコントラクトを参照するときにこれらの関数を表示する。

**@view**


Functions with the `@view` decorator are not allowed to change state variables. In fact, the compiler will reject the entire program (with an appropriate error) if the function tries to change a state variable.

`@view`デコレータを付けた関数は状態変数を変更できない。実際、このデコレータが付いた関数が状態変数を更新しようとすると、コンパイラはプログラム全体を（適切なエラーで）拒否する。

**@pure**


Functions with the `@pure` decorator are not allowed to read any blockchain state or make a call to nonpure methods or to other contracts.

`@pure`デコレータを付けた関数は、ブロックチェーンの状態を読み取ったり、pureでないメソッドや他のコントラクトを呼び出したりすることができない。

**@payable**


Only functions with the `@payable` decorator are allowed to transfer value.

`@payable`デコレータを持つ関数のみがバリューを転送できる。

**@deploy**


The `@deploy` decorator is used to mark the constructor function of a contract. This function runs exactly once when the contract is deployed to the blockchain, typically for setting up initial state variables and configuration. In Vyper, only the `__init__()` function can be marked with `@deploy`, and this decorator is required if you want to include constructor logic in your contract.

`@deploy`デコレータは、コントラクトのコンストラクタ関数をマークするために使用される。この関数はコントラクトがブロックチェーンにデプロイされるときに1度だけ実行され、通常は初期状態変数や設定のセットアップに用いられる。Vyperでは`__init__()`関数のみに`@deploy`を付けることができ、コントラクトにコンストラクタロジックを含める場合はこのデコレータが必須である。

**@raw_return**


Functions with the `@raw_return` decorator return raw bytes without applying ABI encoding. This decorator is particularly useful in proxy contracts and helper contracts where you need to forward the exact output of another contract call without wrapping it in another layer of encoding. However, there are important limitations: this decorator can be used only on `@external` functions. It cannot be used in interface definitions, and when calling such functions from other contracts, you should use `raw_call` instead of interface calls since the return data may not be ABI encoded.

`@raw_return`デコレータを付けた関数は、ABIエンコーディングを適用せずに生のバイト列を返す。このデコレータは、別のコントラクト呼び出しの出力をエンコーディングの追加層で包むことなくそのまま転送する必要があるプロキシコントラクトやヘルパーコントラクトにおいて特に有用である。ただし、重要な制限がある。このデコレータは`@external`関数にのみ使用でき、インターフェース定義では使用できない。また、他のコントラクトからこのような関数を呼び出す場合は、戻り値がABIエンコードされていない可能性があるため、インターフェース呼び出しではなく`raw_call`を使用する必要がある。

**@nonreentrant**


The `@nonreentrant` decorator places a lock on a function, preventing reentrant calls to any function covered by the decorator. The reentrancy lock ensures that such functions cannot be entered again until they have finished executing. This decorator is used to prevent reentrancy attacks, where an external contract might call back into the protected functions, potentially causing unexpected behavior or contract exploits. Vyper also supports a pragma for nonreentrancy by default, making all external functions nonreentrant unless explicitly overridden. For example, if contract A uses this decorator for reentrancy protection and makes an external call to contract B, any attempt by contract B to call back into a protected function on contract A will cause the transaction to revert.

`@nonreentrant`デコレータは関数にロックをかけ、そのデコレータが適用されたすべての関数に対するリエントラント呼び出しを防止する。リエントランシーロックにより、対象の関数は実行が完了するまで再度呼び出すことができない。このデコレータは、外部コントラクトが保護された関数にコールバックし、予期しない動作やコントラクトの悪用を引き起こす可能性があるリエントランシー攻撃を防ぐために使用される。Vyperはデフォルトでリエントランシー防止のプラグマもサポートしており、明示的にオーバーライドしない限り、すべての外部関数がリエントラント不可となる。たとえば、コントラクトAがリエントランシー保護のためにこのデコレータを使用し、コントラクトBに外部呼び出しを行った場合、コントラクトBがコントラクトAの保護された関数にコールバックしようとすると、トランザクションはリバートされる。

> **注記**
>
> Vyperバージョン0.2.15、0.2.16、および0.3.0のnonreentrant機能には、2023年半ばに発見され、Curveプロトコルへの攻撃に悪用された重大なバグが含まれていた。リエントランシーの脆弱性については9章で詳しく取り上げる。


Vyper implements the logic of decorators explicitly. For example, the Vyper compilation process will fail if a function has both a `@payable` decorator and a `@view` decorator. This makes sense because a function that transfers value has by definition updated the state so cannot be `@view`. Each Vyper function must be decorated with either `@external` or `@internal` (but not both!).

　Vyperはデコレータのロジックを明示的に実装しています。たとえば、ある関数が`@payable`デコレータと`@view`デコレータの両方を持っている場合、Vyperのコンパイルは失敗します。バリューを転送する関数はその定義上、状態を更新するため、`@view`にはなりえません。Vyperの関数には`@external`もしくは`@internal`のどちらかのデコレータを付ける必要があります（ただし両方は不可です）。

## Function and Variable Ordering

## 関数と変数の順序


Vyper's approach to scoping and declarations follows C99 scoping rules, which provide more flexibility than you might initially expect. While Vyper contracts must still be contained within a single file (unless you are using the module system), the strict ordering requirements that were present in earlier versions have been relaxed for module-scope declarations.

　Vyperのスコーピングと宣言に対するアプローチはC99のスコーピング規則に従っており、最初に思うよりも柔軟性があります。Vyperのコントラクトは依然として単一のファイル内に収める必要がありますが（モジュールシステムを使用しない場合）、以前のバージョンに存在した厳密な順序の要件は、モジュールスコープの宣言に関しては緩和されています。


Variables and functions that are declared at the module scope (outside of any function body) are visible throughout the entire contract, even before their formal declaration. This means you can reference state variables and call functions before they appear in the file, similar to how many modern programming languages handle forward declarations.

　モジュールスコープ（関数本体の外側）で宣言された変数や関数は、正式な宣言よりも前であっても、コントラクト全体から参照できます。つまり、多くの現代的なプログラミング言語が前方宣言を扱うのと同様に、状態変数の参照や関数の呼び出しを、それらがファイルに記述される前に行うことができます。


Here's a practical example showing how scoping works in modern Vyper:

　現代のVyperにおけるスコーピングの動作を示す実用的な例を見てみましょう。

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


However, within function scope, Vyper still maintains strict ordering rules. Local variables must be declared before use, and you cannot shadow the names of constants, immutable variables, or other module-level declarations with local variables. This scoping approach strikes a balance between Python's flexibility and the needs of smart contract development, where clear visibility of state variables and function relationships is important for security auditing.

　ただし、関数スコープ内では、Vyperは依然として厳密な順序規則を維持しています。ローカル変数は使用する前に宣言する必要があり、定数やイミュータブル変数、その他のモジュールレベルの宣言の名前をローカル変数でシャドーイングすることはできません。このスコーピングのアプローチは、Pythonの柔軟性と、状態変数や関数の関係の明確な可視性がセキュリティ監査にとって重要であるスマートコントラクト開発のニーズとのバランスを取っています。

## Compilation

## コンパイル


The easiest way to experiment with Vyper is to use the [Remix online compiler](https://remix.ethereum.org), which allows you to write and then compile your smart contracts using only your web browser (you will need to activate the vyper-remix plug-in in the plug-in manager).

　Vyperを試す最も簡単な方法は、[Remixオンラインコンパイラ](https://remix.ethereum.org)を使うことです。Webブラウザだけを用いてスマートコントラクトを作成し、コンパイルできます（プラグインマネージャでvyper-remixプラグインを有効化する必要があります）。

> **注記**
>
> Vyperには[組み込みの共通インターフェース](https://oreil.ly/GazPW)（ERC-20やERC-721など）が付属しており、これらのコントラクトとのやりとりをすぐに利用できる。Vyperにおけるコントラクトはグローバル変数として宣言する必要がある。ERC-20変数の宣言例は次のとおりである。
> `from vyper.interfaces import ERC20` `token: ERC20`


You can also compile a contract using the command line. Each Vyper contract is saved in a file with the *.vy* extension. Once Vyper is installed, you can compile a contract by running the following command:

　コマンドラインからコントラクトをコンパイルすることもできます。Vyperのコントラクトはそれぞれ *.vy* 拡張子のファイルに保存されます。Vyperをインストールすれば、次のコマンドでコントラクトをコンパイルできます。

```bash
vyper ~/hello_world.vy
```


The compiler offers extensive output options. To get the human-readable ABI description in JSON format, use:

　コンパイラは豊富な出力オプションを提供しています。人間が読みやすいJSON形式のABI記述を取得するには、次のコマンドを使用します。

```bash
vyper -f abi ~/hello_world.vy
```


For development and testing, you'll likely want additional outputs like bytecode, opcodes, or interface files. The compiler supports numerous output formats:

　開発やテストでは、バイトコード、オペコード、インターフェースファイルなどの追加出力が必要になることもあるでしょう。コンパイラは多数の出力フォーマットをサポートしています。

```bash
vyper -f abi,bytecode,interface,source_map ~/hello_world.vy
```


Modern Vyper also includes advanced optimization modes. You can optimize for gas efficiency with `--optimize gas` (the default) or for smaller contract sizes with `--optimize codesize`. The newer, experimental Venom IR pipeline can be enabled with `--experimental-codegen` for even better optimizations.

　現代のVyperには高度な最適化モードも含まれています。`--optimize gas`（デフォルト）でガス効率を最適化するか、`--optimize codesize`でコントラクトサイズを小さくすることができます。新しい実験的なVenom IRパイプラインは`--experimental-codegen`で有効化でき、さらに優れた最適化が可能です。


While Remix and the command-line compiler are excellent for learning and experimentation, developers working on larger projects typically need comprehensive development frameworks. [ApeWorx](https://oreil.ly/AJRSa) (formerly Ape) provides excellent Vyper support with features like automated testing, deployment scripting, and integration with various networks. [Foundry](https://oreil.ly/CWIKj), while primarily focused on Solidity, also supports Vyper development and offers powerful testing and simulation capabilities. These frameworks provide the kind of mature development environment that professional smart contract developers need for building complex applications.

　Remixやコマンドラインコンパイラは学習や実験に最適ですが、大規模なプロジェクトに取り組む開発者は通常、包括的な開発フレームワークを必要とします。[ApeWorx](https://oreil.ly/AJRSa)（旧Ape）は、自動テスト、デプロイスクリプティング、さまざまなネットワークとの統合といった機能を備え、Vyperを優れたかたちでサポートしています。[Foundry](https://oreil.ly/CWIKj)は主にSolidity向けですが、Vyperの開発もサポートしており、強力なテストおよびシミュレーション機能を提供しています。これらのフレームワークは、複雑なアプリケーションを構築するプロフェッショナルなスマートコントラクト開発者に必要な、成熟した開発環境を提供します。

## Protecting Against Overflow Errors at the Compiler Level

## コンパイラレベルでのオーバーフローエラーに対する保護


Overflow errors in software can be catastrophic when dealing with real value. For example, one [transaction from mid-April 2018](https://oreil.ly/zOy06) shows the malicious transfer of more than 57,896,044,618,658,100,000,000,000,000,000,000,000,000, 000,000,000,000,000,000 BEC tokens. This transaction was the result of an integer-overflow issue in Beauty Chain's ERC-20 token contract (*BecToken.sol*).

　ソフトウェアにおけるオーバーフローエラーは、実際の価値を扱う場合に破滅的な結果をもたらすことがあります。たとえば、[2018年4月中旬のあるトランザクション](https://oreil.ly/zOy06)は、57,896,044,618,658,100,000,000,000,000,000,000,000,000,000,000,000,000,000,000を超えるBECトークンの不正な移転を示しています。このトランザクションは、Beauty ChainのERC-20トークンコントラクト（*BecToken.sol*）における整数オーバーフロー問題の結果でした。


One of the core features of Vyper has always been its built-in overflow protection, which mitigates the risk of the overflow errors that have historically plagued smart contract development. Vyper's approach to overflow protection is comprehensive: it includes SafeMath-equivalent protection that handles the necessary exception cases for integer arithmetic, ensuring that operations like addition, subtraction, multiplication, and division are safe by default and throwing exceptions when an overflow or underflow occurs. Additionally, Vyper uses clamps to enforce value limits whenever a literal constant is loaded, a value is passed to a function, or a variable is assigned.

　Vyperのコア機能の1つは、スマートコントラクト開発を歴史的に悩ませてきたオーバーフローエラーのリスクを軽減する、組み込みのオーバーフロー保護です。Vyperのオーバーフロー保護へのアプローチは包括的であり、整数演算に関する例外ケースを処理するSafeMath相当の保護を含んでいます。これにより、加算、減算、乗算、除算などの操作がデフォルトで安全であることが保証され、オーバーフローやアンダーフローが発生した場合は例外がスローされます。さらに、Vyperは定数リテラルが読み込まれたり、関数に値が渡されたり、変数に値が割り当てられるたびに、クランプを使って値の制限を強制します。


It's worth noting that recent versions of Solidity (0.8.0 and later) have also integrated native overflow checks at the compiler level, similar to what Vyper has provided from the beginning. This means that arithmetic operations in modern Solidity now automatically include overflow checks, significantly reducing the risk of overflow errors without requiring additional libraries like SafeMath. While this change has brought Solidity closer to Vyper's safety-first approach, Vyper's implementation remains more comprehensive, including the clamp operations and more consistent bounds checking throughout the language. The key difference is philosophical: Vyper was designed from the ground up with overflow protection as a core principle, while Solidity added it as an enhancement to address historical vulnerabilities. This difference in approach reflects Vyper's broader commitment to making unsafe code harder to write by default.

　注目すべきは、Solidityの最近のバージョン（0.8.0以降）でも、Vyperが当初から提供してきたものと同様のネイティブなオーバーフローチェックがコンパイラレベルで統合されていることです。これにより、現代のSolidityでは算術演算にオーバーフローチェックが自動的に含まれるようになり、SafeMathのような追加ライブラリを必要とせずにオーバーフローエラーのリスクが大幅に低減されています。この変更によりSolidityはVyperのセキュリティ最優先のアプローチに近づきましたが、Vyperの実装はクランプ操作や言語全体にわたるより一貫した境界チェックを含め、依然としてより包括的です。根本的な違いは思想にあります。Vyperはオーバーフロー保護をコア原則として最初から設計されたのに対し、Solidityは歴史的な脆弱性に対処するための拡張として追加しました。このアプローチの違いは、安全でないコードをデフォルトで書きにくくするというVyperのより広い取り組みを反映しています。

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
