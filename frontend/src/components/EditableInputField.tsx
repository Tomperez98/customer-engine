'use client'

import {ChangeEvent, useCallback, useEffect, useState} from 'react'
import {MdEditSquare, MdCancel} from 'react-icons/md'
import {InputName, Template} from '@/types/Inputs'
import Input from './Input'
import RichTextEditor from './RichTextEditor'
import IconButton from './IconButton'

interface EditableInputFieldProps {
    fieldName: InputName
    originalValue: string | string[]
    isEditingTemplate: boolean
    label: string
    setIsEditingTemplate: (isEditingTemplate: boolean) => void
    setTemplate: any
    template: Template
    type: 'input' | 'textarea'
    souldForceReset?: boolean
}

const EditableInputField = ({
    fieldName,
    template,
    isEditingTemplate,
    label,
    originalValue,
    setIsEditingTemplate,
    setTemplate,
    type,
    souldForceReset,
}: EditableInputFieldProps) => {
    const [isEditing, setIsEditing] = useState<boolean>(false)

    const handleEditField = () => {
        if (!isEditingTemplate) {
            setIsEditingTemplate(true)
        }
        setIsEditing(true)
    }

    const handleInputFieldChange = useCallback(
        (
            event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
            name: InputName
        ) => {
            setTemplate({...template, [name]: event.target.value})
        },
        [template, setTemplate]
    )

    const handleReset = () => {
        setIsEditing(false)
        setTemplate({...template, [fieldName]: originalValue})
    }

    useEffect(() => {
        if (souldForceReset) {
            setIsEditing(false)
        }
    }, [souldForceReset])

    const getInputElement = useCallback(() => {
        if (type === 'input') {
            return (
                <Input
                    name={fieldName}
                    onChange={handleInputFieldChange}
                    value={(template as any)[fieldName] || ''}
                />
            )
        }
        if (type === 'textarea') {
            return (
                <RichTextEditor
                    name={fieldName as any}
                    onChange={handleInputFieldChange}
                    value={(template as any)[fieldName] || ''}
                />
            )
        }
        return null
    }, [fieldName, template, handleInputFieldChange, type])

    return (
        <div className='mb-1 w-full'>
            <div className='flex flex-row items-center gap-2'>
                <label
                    htmlFor={fieldName}
                    className='text-lg font-semibold capitalize text-neutral-800'>
                    {label}
                </label>
                {isEditing ? (
                    <IconButton
                        Icon={MdCancel}
                        onClick={handleReset}
                        size='text-lg'
                        tooltip='Cancelar'
                    />
                ) : (
                    <IconButton
                        Icon={MdEditSquare}
                        onClick={handleEditField}
                        tooltip='Editar'
                        size='text-lg'
                    />
                )}
            </div>
            {isEditing ? (
                getInputElement()
            ) : (
                <p className='break-words'>{(template as any)[fieldName]}</p>
            )}
        </div>
    )
}

export default EditableInputField
