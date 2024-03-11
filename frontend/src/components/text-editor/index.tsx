import {useCallback, useState} from 'react'
import classNames from 'classnames'
import {useEditor, EditorContent, Editor} from '@tiptap/react'
import Document from '@tiptap/extension-document'
import Paragraph from '@tiptap/extension-paragraph'
import Text from '@tiptap/extension-text'
import Bold from '@tiptap/extension-bold'
import Underline from '@tiptap/extension-underline'
import Italic from '@tiptap/extension-italic'
import Strike from '@tiptap/extension-strike'
import Code from '@tiptap/extension-code'
import History from '@tiptap/extension-history'
import * as Icons from './icons'
import './styles.css'

interface SimpleEditorProps {
    content: string
}

const SimpleEditor = ({content}: SimpleEditorProps) => {
    const [editorContent, setEditorContent] = useState('')
    const editor = useEditor({
        extensions: [
            Document,
            History,
            Paragraph,
            Text,
            Bold,
            Underline,
            Italic,
            Strike,
            Code,
        ],
        content,
        onUpdate({editor}) {
            setEditorContent(editor.getHTML())
        },
    }) as Editor

    const toggleBold = useCallback(() => {
        editor.chain().focus().toggleBold().run()
    }, [editor])

    const toggleUnderline = useCallback(() => {
        editor.chain().focus().toggleUnderline().run()
    }, [editor])

    const toggleItalic = useCallback(() => {
        editor.chain().focus().toggleItalic().run()
    }, [editor])

    const toggleStrike = useCallback(() => {
        editor.chain().focus().toggleStrike().run()
    }, [editor])

    const toggleCode = useCallback(() => {
        editor.chain().focus().toggleCode().run()
    }, [editor])

    if (!editor) {
        return null
    }

    return (
        <div className='editor'>
            <div className='menu'>
                <button
                    className='menu-button'
                    onClick={() => editor.chain().focus().undo().run()}
                    disabled={!editor.can().undo()}>
                    <Icons.RotateLeft />
                </button>
                <button
                    className='menu-button'
                    onClick={() => editor.chain().focus().redo().run()}
                    disabled={!editor.can().redo()}>
                    <Icons.RotateRight />
                </button>
                <button
                    className={classNames('menu-button', {
                        'is-active': editor.isActive('bold'),
                    })}
                    onClick={toggleBold}>
                    <Icons.Bold />
                </button>
                <button
                    className={classNames('menu-button', {
                        'is-active': editor.isActive('underline'),
                    })}
                    onClick={toggleUnderline}>
                    <Icons.Underline />
                </button>
                <button
                    className={classNames('menu-button', {
                        'is-active': editor.isActive('intalic'),
                    })}
                    onClick={toggleItalic}>
                    <Icons.Italic />
                </button>
                <button
                    className={classNames('menu-button', {
                        'is-active': editor.isActive('strike'),
                    })}
                    onClick={toggleStrike}>
                    <Icons.Strikethrough />
                </button>
                <button
                    className={classNames('menu-button', {
                        'is-active': editor.isActive('code'),
                    })}
                    onClick={toggleCode}>
                    <Icons.Code />
                </button>
            </div>
            <EditorContent editor={editor} />
        </div>
    )
}

export default SimpleEditor
