'use client'

import {ChangeEvent, useEffect, useState} from 'react'
import {MdEdit} from 'react-icons/md'
import {FormKey, FormTemplate} from '@/types/Forms'
import {MdAddCircle} from 'react-icons/md'
import {MdDelete} from 'react-icons/md'
import IconButton from './IconButton'

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
                <h2 className='text-lg font-semibold capitalize text-slate-800'>
                    {label}
                </h2>
                {isEditing || editableOnly ? (
                    <div className='flex flex-row items-center gap-2'>
                        <IconButton
                            onClick={handleAddSubField}
                            Icon={MdAddCircle}
                            size='text-lg'
                        />
                        {!editableOnly && (
                            <button onClick={handleReset}>reset</button>
                        )}
                    </div>
                ) : (
                    <IconButton onClick={handleEditField} Icon={MdEdit} />
                )}
            </div>
            <div className='flex w-full flex-col gap-2'>
                {currentField?.map((field: string, idx: number) => {
                    return isEditing || editableOnly ? (
                        <div
                            key={idx}
                            className='flex w-full max-w-full flex-row items-center gap-2'>
                            <input
                                className='my-2  flex-grow rounded-md border-2 border-gray-300 px-1 text-slate-500'
                                onChange={(e) => handleSubFieldChange(e, idx)}
                                value={currentField[idx]}
                            />
                            {currentField.length > 1 && idx > 0 && (
                                <div className='shrink-0'>
                                    <IconButton
                                        onClick={() =>
                                            handleRemoveSubField(idx)
                                        }
                                        Icon={MdDelete}
                                        size='text-lg'
                                        fill='text-red-500'
                                    />
                                </div>
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
