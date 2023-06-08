import { useState } from 'react';

function Input({name, placeholder, width}) {
    return (
        <input name={name} className={`font-math rounded-md text-s my-input h-12 ${width}`} type="text" placeholder={placeholder}></input>
    )
}

function Fx({type, id, funcs, setter}) {
    const remove = () => {
        setter(funcs.filter(e => e !== id));
    }
    const deleteBtn =
        <button onClick={remove} type="button" className="hover:brightness-90">
            <img className="p-2" alt="del" src={process.env.PUBLIC_URL + "/assets/garbage.svg"}/>
        </button>

    return (
        <div className="flex flex-row gap-4">
            {type === "Functions"
                ? <Input name="a-function" placeholder="E.g. f(x) = 2x ..." width="w-1/2"></Input>
                : <div className="flex flex-row gap-4 max-w-fit">
                    <Input name="constant-name" width="w-1/3"placeholder="name"></Input>
                    <span className="text-rose-100 bold text-xl self-center">=</span>
                    <Input name="constant-value" width="w-1/3" placeholder="value"></Input>
                    {deleteBtn}
                </div>
            }
            {type === "Functions" ? deleteBtn : ""}
        </div>
    )
}

export default function List({type}) {
    let list = [];
    const [ funcs, setFunctions ] = useState(list);

    const add = () => {
        const element = funcs.length > 0 ? funcs[funcs.length - 1] + 1 : 0;
        setFunctions([...funcs, element]);
    }

    return (
        <div className="flex flex-col gap-3">
            <h1 className="my-h1">{type}</h1>
            {funcs.map(id => {
                return (
                    <Fx type={type} id={id} key={id} funcs={funcs} setter={(x) => setFunctions(x) }/>
                )
            })}
            <button className="flex justify-center w-[50%] p-2 rounded-md bg-red-800" type="button" onClick={add}>
                <img alt="+" src={process.env.PUBLIC_URL + "/assets/plus.svg"}/>
            </button>
        </div>
    )
}