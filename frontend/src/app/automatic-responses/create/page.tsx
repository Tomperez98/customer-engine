'use client'

import EditableListField from '@/components/EditableListField'
import Layout from '@/components/layout'
import {FORM_TEMPLATE, INPUT_FIELDS} from '@/constants/formFields'
import useCreateForm from '@/hooks/useCreateForm'
import {useCallback, useState} from 'react'

const CreateForm = () => {
    const [formTemplate, setFormTemplate] = useState(FORM_TEMPLATE)
    const {submit} = useCreateForm(formTemplate)
    const handleInputFieldChange = useCallback((event, name) => {
        setFormTemplate((prevState) => ({
            ...prevState,
            [name]: event.target.value,
        }))
    }, [])

    const getInputElement = useCallback(
        (field, idx) => {
            const {name, component, label} = field

            if (component === 'input') {
                return (
                    <div key={idx} className='flex flex-col'>
                        <label
                            htmlFor={name}
                            className='text-lg font-extrabold capitalize text-slate-800'>
                            {label}
                        </label>
                        <input
                            name={name}
                            className='rounded-md border-2 border-gray-300 px-1 text-slate-500'
                            onChange={(e) => handleInputFieldChange(e, name)}
                            value={formTemplate[name] || ''}
                        />
                    </div>
                )
            }
            if (component === 'textarea') {
                return (
                    <div key={idx} className='flex flex-col'>
                        <label
                            htmlFor={name}
                            className='text-lg font-extrabold capitalize text-slate-800'>
                            {label}
                        </label>
                        <textarea
                            name={name}
                            className='rounded-md border-2 border-gray-300 px-1 text-slate-500'
                            onChange={(e) => handleInputFieldChange(e, name)}
                            value={formTemplate[name] || ''}
                        />
                    </div>
                )
            }
            if (component === 'list') {
                return (
                    <EditableListField
                        editedForm={formTemplate}
                        setEditedForm={setFormTemplate}
                        key={idx}
                        fieldName={name}
                        label={label}
                        originalValue={formTemplate[name]}
                        editableOnly
                    />
                )
            }
            return null
        },
        [formTemplate, handleInputFieldChange]
    )

    console.log(formTemplate)

    return (
        <Layout>
            <section className='flex flex-col'>
                <h1 className='mb-4 text-3xl font-extrabold text-slate-800'>
                    Crear formulario
                </h1>
                <div className='w-full rounded-md bg-white p-8 shadow-md'>
                    {INPUT_FIELDS.map((field, idx) => {
                        return getInputElement(field, idx)
                    })}
                    <div className='flex w-full flex-row items-center justify-end gap-2'>
                        <button>Descartar</button>
                        <button
                            className='disabled:text-gray-300'
                            onClick={async () => await submit()}>
                            Guardar
                        </button>
                    </div>
                </div>
            </section>
        </Layout>
    )
}

export default CreateForm
