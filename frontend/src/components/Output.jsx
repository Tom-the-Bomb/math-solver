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
        <div className="flex flex-col gap-4">
            <h1 className="text-red-100 text-lg my-h1">{name}</h1>
            <div className="flex flex-row justify-between font-mono p-4 rounded-md bg-rose-800 text-rose-300">
                <div>
                    {content.map((x, i) => latex ? <Latex key={i} content={x}></Latex> : content)}
                </div>
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
    )
}

export default function Output({response}) {
    if (response) {
        if (!response.ok) {
            return (
                <div className="mt-10">
                    <Section name="Error" content={[response.content.error]}></Section>
                </div>
            )
        }
        const domain = `\\text{Domain}\\in${response.content.domain}`
        const range = `\\text{Range}\\in${response.content.range}`

        const equation = response.content.equation;
        let simplified = response.content.simplified_equation;
        simplified = equation === simplified
            ? [equation]
            : ['\\text{false}', '\\text{true}'].includes(equation.toLowerCase())
            ? [simplified, equation]
            : [equation, simplified];

        let max = response.content.max
        let min = response.content.min
        max = max ? `\\text{Maxima @ }${max}` : ''
        min = min ? `\\text{Minima @ }${min}` : ''

        return (
            <div className="flex flex-col gap-4 mt-10">
                <Section latex={true} name="Domain & Range" content={[domain, range]}></Section>
                <Section latex={true} name="Simplified" content={simplified}></Section>
                <Section latex={true} name="Solution" content={[response.content.latex_solution]}></Section>
                <Section latex={true} name="Derivative" content={[response.content.derivative]}></Section>
                <Section latex={true} name="Maxima & Minima" content={[max, min]}></Section>
            </div>
        )
    } else {
        return (
            <p className="text-rose-300 text-2xl mt-10 bold">Enter some math first...</p>
        )
    }
}