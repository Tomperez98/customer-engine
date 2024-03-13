'use client'

import {ChangeEvent, useEffect, useState} from 'react'
import {MdEdit} from 'react-icons/md'
import {FormKey, FormTemplate} from '@/types/Forms'

interface EditableListFieldProps {
    fieldName: FormKey
    isEditingForm?: boolean
    setIsEditingForm?: (isEditingForm: boolean) => void
    editable?: boolean
    setTemplateForm: (formTemplate: FormTemplate) => void
    templateForm: FormTemplate
    originalValue: string | string[]
    label: string
    editableOnly?: boolean
    souldForceReset?: boolean
}

const EditableListField = ({
    fieldName,
    isEditingForm,
    setIsEditingForm,
    setTemplateForm,
    templateForm,
    originalValue,
    label,
    editableOnly,
    souldForceReset,
}: EditableListFieldProps) => {
    const [isEditing, setIsEditing] = useState<boolean>(false)
    const currentField = templateForm[fieldName] as string[]

    const handleEditField = () => {
        if (!isEditingForm) {
            setIsEditingForm?.(true)
        }
        setIsEditing(true)
    }

    const handleSubFieldChange = (
        e: ChangeEvent<HTMLInputElement>,
        idx: number
    ) => {
        setTemplateForm({
            ...templateForm,
            [fieldName]: currentField.map((field: string, subIdx: number) => {
                if (subIdx === idx) {
                    return e.target.value
                }
                return field
            }),
        })
    }

    const handleAddSubField = () => {
        setTemplateForm({
            ...templateForm,
            [fieldName]: [...currentField, ''],
        })
    }

    const handleRemoveSubField = (idx: number) => {
        if (currentField.length > 1) {
            setTemplateForm({
                ...templateForm,
                [fieldName]: currentField.filter(
                    (_, filterIdx) => filterIdx !== idx
                ),
            })
        }
    }

    const handleReset = () => {
        setIsEditing(false)
        setTemplateForm({...templateForm, [fieldName]: originalValue})
    }

    useEffect(() => {
        if (souldForceReset) {
            setIsEditing(false)
        }
    }, [souldForceReset])

    return (
        <div className='mb-1'>
            <div className='flex flex-row items-center gap-2'>
                <h2 className='text-lg font-extrabold capitalize text-slate-800'>
                    {label}
                </h2>
                {isEditing || editableOnly ? (
                    <div className='flex flex-row gap-2'>
                        <button onClick={handleAddSubField}>add</button>
                        {!editableOnly && (
                            <button onClick={handleReset}>reset</button>
                        )}
                    </div>
                ) : (
                    <MdEdit
                        className='cursor-pointer'
                        onClick={handleEditField}
                    />
                )}
            </div>
            <div className='flex flex-col gap-2'>
                {currentField?.map((field: string, idx: number) => {
                    return isEditing || editableOnly ? (
                        <div key={idx}>
                            <input
                                className='mr-2 w-11/12 rounded-md border-2 border-gray-300 px-1 text-slate-500'
                                onChange={(e) => handleSubFieldChange(e, idx)}
                                value={currentField[idx]}
                            />
                            {currentField.length > 1 && (
                                <button
                                    onClick={() => handleRemoveSubField(idx)}>
                                    delete
                                </button>
                            )}
                        </div>
                    ) : (
                        <p key={idx}>{field}</p>
                    )
                })}
            </div>
        </div>
    )
}

export default EditableListField
