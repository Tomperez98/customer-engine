'use client'
import Layout from '@/components/layout'
import useGetForms from '@/hooks/useGetForms'
import React, {useEffect, useMemo, useState} from 'react'
import {Form, FormKey, FormKeys} from '@/types/Forms'
import useEditForm from '@/hooks/useEditForm'
import EditableInputField from '@/components/EditableInputField'
import EditableListField from '@/components/EditableListField'
import {FORM_TEMPLATE, INPUT_FIELDS} from '@/constants/formFields'

const VISIBLE_FIELDS = ['automatic_response_id', 'examples', 'name', 'response']

const FormDetail = ({params}: {params: {'automatic-response-id': string}}) => {
    const {'automatic-response-id': formId} = params
    const {data, isLoading} = useGetForms(formId)
    const [isEditingForm, setIsEditingForm] = useState<boolean>(false)
    const [editFormTemplate, setEditFormTemplate] = useState<any>(FORM_TEMPLATE)
    const {
        submit,
        isLoading: isUpdateLoading,
        error,
    } = useEditForm(formId, editFormTemplate as Form)

    const formData = useMemo(() => data?.automatic_response as Form, [data])

    const relevantData = useMemo(() => {
        return Object.keys(FORM_TEMPLATE).reduce(
            (acc, key) => {
                if (data?.automatic_response?.hasOwnProperty(key)) {
                    acc[key] = formData[key as FormKey]
                }
                return acc
            },
            {} as {[key: string]: string | string[]}
        )
    }, [data, formData])

    useEffect(() => {
        if (data) {
            setEditFormTemplate({...relevantData})
        }
    }, [data, relevantData])

    return (
        <Layout>
            <section className='flex flex-col'>
                <h1 className='mb-4 text-3xl font-extrabold text-slate-800'>
                    Detalles de formulario
                </h1>
                <div className='w-full rounded-md bg-white p-8 shadow-md'>
                    {data && (
                        <>
                            <label
                                htmlFor='automatic_response_id'
                                className='text-lg font-extrabold capitalize text-slate-800'>
                                {FormKeys['automatic_response_id']}
                            </label>
                            <p>{formData?.automatic_response_id}</p>
                            {INPUT_FIELDS.map((field, idx: number) => {
                                if (
                                    field.component === 'input' ||
                                    field.component === 'textarea'
                                ) {
                                    return (
                                        <EditableInputField
                                            editedForm={editFormTemplate}
                                            setEditedForm={setEditFormTemplate}
                                            isEditingForm={isEditingForm}
                                            fieldName={field.name}
                                            label={field.label}
                                            originalValue={
                                                formData[field?.name]
                                            }
                                            key={idx}
                                            setIsEditingForm={setIsEditingForm}
                                        />
                                    )
                                }

                                return (
                                    <EditableListField
                                        editedForm={editFormTemplate}
                                        setEditedForm={setEditFormTemplate}
                                        editable={field.editable}
                                        isEditingForm={isEditingForm}
                                        key={idx}
                                        fieldName={field?.name}
                                        label={field.label}
                                        originalValue={formData[field?.name]}
                                        setIsEditingForm={setIsEditingForm}
                                    />
                                )
                            })}
                        </>
                    )}
                    {isEditingForm && (
                        <div className='flex w-full flex-row items-center justify-end gap-2'>
                            <button>Descartar</button>
                            <button
                                className='disabled:text-gray-300'
                                onClick={async () => await submit()}>
                                Guardar
                            </button>
                        </div>
                    )}
                </div>
            </section>
        </Layout>
    )
}

export default FormDetail
