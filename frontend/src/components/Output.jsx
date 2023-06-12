import { useRef, useEffect, useState } from "react";

var katex = require('katex');

function Latex({content}) {
    const container = useRef();

    useEffect(() => {
        katex.render(content, container.current, { throwOnError: false });
    }, [content]);

    return <div ref={container} />
}

function Section({latex, name, content}) {
    const isGraph = name === "Graph";
    const [ copyClicked, setCopyClicked ] = useState(false);

    const delay = ms => new Promise(
        resolve => setTimeout(resolve, ms)
    );

    const copyClick = async (content) => {
        navigator.clipboard.writeText(content.join("\n"));

        setCopyClicked(true);
        await delay(1000);
        setCopyClicked(false);
    }

    return (
        <details open className="[&_img.arrow-cls]:open:-rotate-180">
            <summary className={`flex items-center gap-4 border-b-2 ${ isGraph ? "py-2 pt-6" : "py-2"} border-rose-500`}>
                <h1 className="text-red-100 text-lg my-h1">{name}</h1>
                <img
                    className="arrow-cls rotate-0 transform text-blue-700 transition-all duration-300"
                    src={process.env.PUBLIC_URL + "/assets/arrow.svg"} alt=">"
                />
            </summary>
            { !isGraph
                ? <div className="mt-4 scrollbar-latex overflow-x-auto flex flex-row flex-wrap gap-y-4 justify-between
                    font-mono p-4 rounded-md bg-rose-800 text-rose-300"
                >
                    <div>
                        {content.map((x, i) => latex ? <Latex key={i} content={x}></Latex> : content)}
                    </div>
                    <div>
                        { copyClicked
                            ? <div className="self-center font-md font-sans text-green-400">Copied!</div>
                            : <button
                                onClick={() => copyClick(content)}
                                type="button"
                                className="rounded-md hover:brightness-[120%] ease-in duration-100 bg-transparent"
                            >
                                <img src={process.env.PUBLIC_URL + "/assets/copy.svg"} alt="copy"/>
                            </button>
                        }
                    </div>
                </div>
                : <div>
                    <p className="text-red-300 my-2">
                        <img className="inline-block mr-2" src={process.env.PUBLIC_URL + "/assets/info.svg"} alt="(i)"/>
                        If the graph is not fully showing or off centered, try entering a domain interval
                        which will be used as the x-axis range
                    </p>
                    <img className="rounded-md mt-4 max-h-[100vh]" src={content} alt="graph"/>
                </div>
            }
        </details>
    )
}

export default function Output({response}) {
    if (response) {
        if (!response.ok || response.content.error !== undefined) {
            return (
                <div className="mt-10">
                    <Section name="Error" content={[response.content.error]}></Section>
                </div>
            )
        }
        const domain = `\\textbf{Domain}\\in${response.content.domain}`
        const range = `\\textbf{Range}\\in${response.content.range}`

        const equation = response.content.equation;
        let simplified = response.content.simplified_equation;
        simplified = equation === simplified
            ? [equation]
            : ['\\text{false}', '\\text{true}'].includes(equation.toLowerCase())
            ? [simplified, equation]
            : [equation, simplified];

        let max = response.content.max
        let min = response.content.min
        max = max ? `\\textbf{Maxima @ }${max}` : ''
        min = min ? `\\textbf{Minima @ }${min}` : ''

        let factored = response.content.factored
        let expanded = response.content.expanded
        factored = factored ? `\\textbf{Factored : }${factored}` : ''
        expanded = expanded ? `\\textbf{Expanded : }${expanded}` : ''

        return (
            response.isGraph
                ? <div>
                    <Section name="Graph" content={response.content.image}></Section>
                </div>
                : <div className="flex flex-col gap-2 mt-10">
                    <Section latex={true} name="Domain & Range" content={[domain, range]}></Section>
                    <Section latex={true} name="Simplified" content={simplified}></Section>
                    <Section latex={true} name="Solution" content={[response.content.latex_solution]}></Section>
                    <Section latex={true} name="Derivative" content={[response.content.derivative]}></Section>
                    <Section latex={true} name="Maxima & Minima" content={[max, min]}></Section>
                    <Section latex={true} name="Factored & Expanded" content={[factored, expanded]}></Section>
                </div>
        )
    } else {
        return (
            <p className="text-rose-300 text-2xl mt-10 bold">Enter some math first...</p>
        )
    }
}