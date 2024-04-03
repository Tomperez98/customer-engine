import {ReactNode} from 'react'
import IconButton from '../IconButton'
import {MdClose} from 'react-icons/md'
import {motion} from 'framer-motion'

interface ModalProps {
    children: ReactNode
    isOpen: boolean
    setIsOpen: (isOpen: boolean) => void
}

const handleContentClick = (event: React.MouseEvent) => {
    event.stopPropagation()
}

const Modal = ({children, isOpen, setIsOpen}: ModalProps) => {
    return (
        <>
            {isOpen && (
                <motion.div
                    initial={{opacity: 0}}
                    animate={{opacity: 1}}
                    exit={{opacity: 0}}
                    className='fixed left-0 top-0 z-50 flex h-screen w-screen cursor-pointer items-center justify-center bg-black bg-opacity-75'
                    onClick={() => setIsOpen(false)}>
                    <div
                        className='relative min-w-64 cursor-auto rounded-md bg-white p-8 shadow-md'
                        onClick={handleContentClick}>
                        <div className='absolute right-4 top-4'>
                            <IconButton
                                size='text-xl'
                                tooltip='Cerrar'
                                Icon={MdClose}
                                onClick={() => setIsOpen(false)}
                            />
                        </div>
                        {children}
                    </div>
                </motion.div>
            )}
        </>
    )
}

export default Modal
