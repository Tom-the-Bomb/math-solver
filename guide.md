# Solver Usage Guide
A guide on the syntax of solver inputs<br>
### Examples
- **Derivative $\frac{d}{dx}{f(x)}$:**<br>
`lim_(h->0)((f(x + h) - f(x)) / h)`<br>
&#8594; $\lim\limits_{h\to0}\frac{f(x+h)-f(x)}{h}$ *(providing that `f(x)` is defined)*
- **Polynomial**<br>
`5x^4 - 3x^3 + 2x - 1.5`<br>
&#8594; $5x^4 - 3x^3 + 2x - 1.5 = 0$
- **Rational**<br>
`(3x + 2)/(2x^2 - 5)`<br>
&#8594; $\frac{3x+2}{2x^2-5} = 0$<br>
- **Sinusoidal**<br>
`sqrt(2)cos(2pi(x + 1/4)) + 5 = 1`<br>
&#8594; $\sqrt{2}\cdot\cos{\left(2\pi\left(x + \frac{1}{4}\right)\right)} + 5 = 1$<br>
- **Logarithmic**<br>
`2log_5(x) + 5 = 2.5`<br>
&#8594; $2\log_{5}{x} + 5 = 2.5$<br>
- **Inequality**<br>
	- `2x + 1 <= -x - 2` &#8594; $2x + 1 \le -x - 2$<br>
	- `3.5x - 2 != 5` &#8594; $3.5x - 2 \ne 5$<br>
- **Euler's identity**<br>
	`e^i*pi + 1 = 0` &#8594; $e^{i\pi} + 1 = 0$<br>
	
See below for specific examples for each **syntax**<br>
### Value limits
For safety purposes
- Default limits
	- **Number literal** $< 9\times10^{25}$
	- **Exponent** $< 256$
	- **Factorial** $< 1024$<br>
### Builtins
Aside from user defined functions & constants, there are builtin ones too:
- **Constants**
	- `e`: Euler's number &#8594; $\approx 2.718$
	- `i`: imaginary unit &#8594; $\sqrt{-1}$
	- `pi`|`π`: pi &#8594; $\approx 3.14$
	- `tau`|`τ`: circle constant &#8594; $2\cdot\pi$
	- `phi`|`φ`|`Φ`: golden ratio  &#8594; $\frac{1 + \sqrt{5}}{2}$
	- `inf`|`infty`|`oo`|`∞`: infinity &#8594; $\infty$
	<br>
- **Functions**
	- Special
		- `eval(x)`<br>
		Expressions are often not pre-evaluated for algebraic equations to maintain accuracy;<br>
        Use to evaluate an expression for it's exact value
		- `lmit(expr, target, to)` | `rt(expr, k)`<br>
		limit and custom-root function aliases for the respective keywords
	*... more*

## Syntax Specifications
This document contains specifications for valid syntax structures and patterns for the solver's parser.<br>
- ### Equation
	Parses an equation; used in the primary equation input.<br>
	An equation is a relation between 2 expressions:<br>
	`<expr> "="|"!="|">"|">="|"<"|"<=" <expr>`<br><br>
	*If only an* `<expr>` *is supplied,*<br>
	*the parser will be default assume that* `<expr> = 0`.<br><br>
	- ### Expression: `<expr>`<br>
		Parses a mathematical expression, this is a general parser node<br>
		used throughout the parser.<br><br>
		- **Unary minus**<br>
			Negates the expression<br>
			Syntax: `"-" <group>`<br>
			> Ex: `-x`<br>
		- **Binary operations**<br>
			Basic binary arithmetic operations <br>
			Syntax: `<expr> "+"|"-"|"*"|"/"|"%"  <expr>` <br>
			> Ex: `2x + 1`<br>
		- **Summation**<br>
			Syntax: `"sum_(" <var> "=" <group>) "^" <group> <group>` <br>
			> Ex: `sum_(x=0)^10 x` &#8594; $\sum\limits_{x=0}^{10}x$<br>
		- **Product**<br>
			Syntax: `"prod_(" <var> "=" <group>) "^" <group> <group>` <br>
			> Ex: `prod_(x=0)^10 x` &#8594; $\prod\limits_{x=1}^{10}x$<br>
		- **Absolute value**<br>
			Syntax: `"|" <expr> "|"`<br>
			> Ex: `|x + 1|` &#8594; $|x + 1|$<br>
			- Can also be used by calling the `abs` function: `abs(x)`<br><br>
		- ### Group: `<group>`<br>
			represents a group of mathematical symbols and terms that can be interpreted together as one group without the need for explicit grouping.<br><br>
			- **Explicit grouping**<br>
				An `<expr>` surrounded by a corresponding pair<br>
				of either `()`, `[]` or `{}`<br><br>
			- **Number** `<number>`<br>
				A numerical value, satisfied by the following regex:<br>
				`/([0-9]+(\.[0-9]*)?|\.[0-9]+)/`<br>
				> Ex: `123`, `14.6`<br>
			- **Variable** `<var>`<br>
				Represents a variable or an *access* of a constant that is included in **builtins** or user defined.<br>
				Syntax: `<identifier>`<br>
				*or* `<identifier> "_" <number>` for associated subscript values.<br>
				> Ex: `x`, `x_0` &#8594; $x_0$<br>
			- **Function Call** `<func>`<br>
			A call to a predefined function, either one included in **builtins** (E.g. `sin`, `floor`...) or a user defined function.<br>
				Syntax: `<identifer> "(" expr, ...")"`<br>
				<br>
				**NOTE:** function calls must be surrounded by explicit parentheses `()` and expressions like `sin x ` are not allowed, instead use `sin(x)`.<br>
				- **Subscripted Function**<br>
                    Syntax: `"_" (number | <var> | <explicit grouping>)`<br>
                    in between the *identifer* and *call* of a standard function call<br>
                    > Ex: `log_x(y)` &#8594; $log_xy$ | `log_(2x)(y)` &#8594; $log_{2x }y$<br>
			- **Exponentiation**<br>
                *Separate from **Binary Operations** as it takes `<group>` for operands.*<br>
                Syntax: `<group> "^" <group>`<br>
                > Ex: `x^3` &#8594; $x^3$<br>
			- **Limit**<br>
                Syntax: `"lim_(" <group> "->" <expr> ")" <group>`<br>
                > Ex: `lim_(h->0)(x + h)` &#8594; $\lim\limits_{h\to0} (x+h)$<br>
			- **Custom root**<br>
                Syntax: `"root" <group> <group>`<br>
                > Ex: `root3(x + 1)` &#8594; $\sqrt[3]{x+1}$<br>
                - Can also be accessed via the `rt` function:<br>
                `rt(x, 3)` &#8594; $\sqrt[3]{x}$<br>
			- **Factorial**<br>
			    Syntax: `"<group>"!"`<br>
                > Ex: `x!` or `(x + 1)!`<br>
                - Can also be accessed via the `factorial` function: `factorial(x)`<br>
			- **Implicit Multiplication** <br>
                Adjacent terms that do not satisfy other parser rules will be inferred to be implicit multiplication:<br>
                Syntax: `<group> <group>`<br>
                > Ex: `3(x + 1)2x` &#8594; $3\cdot\left(x + 1\right)\cdot2\cdot x$<br>

- **Domain**<br>
	Parses a domain expression<br>
	- **Interval** `<Interval>`<br>
		- An mathematical interval notation<br>
		- `<expr>, <expr>` surrounded by either *square brackets* or *parentheses*<br>
		- Ex: `[0, inf)`<br>
	- **Number set** `<number_set>`<br>
		- One of the number sets in mathematics, represented by their full name or their mathematical abbreviation<br>
		- `Complex | Real | Rational | Integer | Whole | Natural`<br>
		- `C | R | Q | Z | W | N`<br>
	- **Compound** `<number_set> "|" <Interval>`<br>
		- An intersection of the above expressions joined by a `|` operator, representing a combination of the above 2 sets.<br>
		- Ex: `R | [0, pi]`<br>
- ### Function
	Parses a declared function expression<br>
	- `<func> "=" <expr>`<br>
		- Ex: `f(x) = 2x + 1`<br>
	- Added to **builtins** and can be later called in the primary equation<br>
- ### Constant
	A custom constant AKA a variable input / alias<br>
	- **name**<br>
	The `name` of the constant, a valid `<var>`<br>
	- **value**<br>
	The value of the constant, any valid number.<br>
	(NO additional parsing is done on this field)