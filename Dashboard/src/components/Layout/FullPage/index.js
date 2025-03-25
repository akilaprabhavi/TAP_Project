import React from 'react';
import './full-page.css';

const Fullpage = ({ onCloseButtonClick }) => {
  return (
    <div className="fullpage">
        <div className='row full-page mx-0 py-4'>
            <div class="col-sm-12 col d-flex justify-content-end px-0 mx-0">
                <i class="fas fa-times" onClick={() => onCloseButtonClick()}></i>
            </div>
        </div>
        <div className='container fp'>
            <div className='row pb-5'>
                <h2 class="menu-title">Global Trade Explorer</h2>
            </div>
            <div className='row pb-5'>
                <div className='col-sm-4'>
                    <div class="card fp">
                        <div class="card-body fp">
                            <img 
                            src="https://www.mckinsey.com/spcontent/bespoke/global-trade-flows/img/menu/map-dark.svg" 
                            class="card-img-top" 
                            alt="Card Image"/>
                            <div className='py-2'>
                                <span className='content-heading'>Who is the top trading partner of each economy?</span>
                            </div>
                            <p class="card-text fp">Trade Partner Map</p>
                        </div>
                    </div>
                </div>
                <div className='col-sm-4'>
                    <div class="card fp">
                        <div class="card-body fp">
                            <img 
                            src="https://www.mckinsey.com/spcontent/bespoke/global-trade-flows/img/menu/map-dark.svg" 
                            class="card-img-top" 
                            alt="Card Image"/>
                            <div className='py-2'>
                                <span className='content-heading'>Who is the top trading partner of each economy?</span>
                            </div>
                            <p class="card-text fp">Trade Partner Map</p>
                        </div>
                    </div>
                </div>
                <div className='col-sm-4'>
                    <div class="card fp">
                        <div class="card-body fp">
                            <img 
                            src="https://www.mckinsey.com/spcontent/bespoke/global-trade-flows/img/menu/map-dark.svg" 
                            class="card-img-top" 
                            alt="Card Image"/>
                            <div className='py-2'>
                                <span className='content-heading'>Who is the top trading partner of each economy?</span>
                            </div>
                            <p class="card-text fp">Trade Partner Map</p>
                        </div>
                    </div>
                </div>
            </div>
            <div className='row pb-4'>
                <div className='col-sm-4'>
                    <div class="card fp">
                        <div class="card-body fp">
                            <img 
                            src="https://www.mckinsey.com/spcontent/bespoke/global-trade-flows/img/menu/map-dark.svg" 
                            class="card-img-top" 
                            alt="Card Image"/>
                            <div className='py-2'>
                                <span className='content-heading'>Who is the top trading partner of each economy?</span>
                            </div>
                            <p class="card-text fp">Trade Partner Map</p>
                        </div>
                    </div>
                </div>
                <div className='col-sm-4'>
                    <div class="card fp">
                        <div class="card-body fp">
                            <img 
                            src="https://www.mckinsey.com/spcontent/bespoke/global-trade-flows/img/menu/map-dark.svg" 
                            class="card-img-top" 
                            alt="Card Image"/>
                            <div className='py-2'>
                                <span className='content-heading'>Who is the top trading partner of each economy?</span>
                            </div>
                            <p class="card-text fp">Trade Partner Map</p>
                        </div>
                    </div>
                </div>
                <div className='col-sm-4'>
                    <div class="card fp">
                        <div class="card-body fp">
                            <img 
                            src="https://www.mckinsey.com/spcontent/bespoke/global-trade-flows/img/menu/map-dark.svg" 
                            class="card-img-top" 
                            alt="Card Image"/>
                            <div className='py-2'>
                                <span className='content-heading'>Who is the top trading partner of each economy?</span>
                            </div>
                            <p class="card-text fp">Trade Partner Map</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div className='container'>
            <div className='row py-5 px-4'>
            <div className='col-sm-12 col-md-12 col-12'>
            <div className='py-2'>
                <span className='content-heading'>Who is the top trading partner of each economy?</span>
            </div>
            <p class="card-text fp">Trade values shown are based on self-reported trade values to UN Comtrade. The accuracy of the data is based on each economy’s reported values. Sector taxonomy and classification are based on the judgment of several industry experts working with McKinsey Global Institute. There are asymmetries in UN Comtrade import and export datasets. See OECD BIMTS for further details. Data used in the visualization is from or ends in 2021. McKinsey & Company expects to update the data as 2022 data becomes available but is under no obligation to update the data or correct the results presented in this visualization.</p>
            </div>
            </div>
        </div>
    </div>
  );
};

export default Fullpage;

